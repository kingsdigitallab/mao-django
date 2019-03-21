"""Near verbatim copy of wagtail.images.models.AbstractImage, only
with the tags field removed, since this caused problems when saving a
new image via an InlinePanel, and the title removed."""

from contextlib import contextmanager
import hashlib
from io import BytesIO
import os.path

from django.conf import settings
from django.core.files import File
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from unidecode import unidecode
from wagtail.admin.utils import get_object_usage
from wagtail.core.models import CollectionMember
from wagtail.images.models import (
    Filter, get_upload_to, ImageQuerySet, SourceImageIOError
)
from wagtail.images.rect import Rect
from wagtail.search import index
from willow.image import Image as WillowImage


class AbstractImage(CollectionMember, index.Indexed, models.Model):
    file = models.ImageField(
        verbose_name=_('file'), upload_to=get_upload_to, width_field='width',
        height_field='height'
    )
    width = models.IntegerField(verbose_name=_('width'), editable=False)
    height = models.IntegerField(verbose_name=_('height'), editable=False)
    created_at = models.DateTimeField(verbose_name=_('created at'),
                                      auto_now_add=True, db_index=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('uploaded by user'),
        null=True, blank=True, editable=False, on_delete=models.SET_NULL
    )

    focal_point_x = models.PositiveIntegerField(null=True, blank=True)
    focal_point_y = models.PositiveIntegerField(null=True, blank=True)
    focal_point_width = models.PositiveIntegerField(null=True, blank=True)
    focal_point_height = models.PositiveIntegerField(null=True, blank=True)

    file_size = models.PositiveIntegerField(null=True, editable=False)
    # A SHA-1 hash of the file contents
    file_hash = models.CharField(max_length=40, blank=True, editable=False)

    objects = ImageQuerySet.as_manager()

    def is_stored_locally(self):
        """
        Returns True if the image is hosted on the local filesystem
        """
        try:
            self.file.path

            return True
        except NotImplementedError:
            return False

    def get_file_size(self):
        if self.file_size is None:
            try:
                self.file_size = self.file.size
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the file subclass, and therefore the
                # storage being used.
                raise SourceImageIOError(str(e))

            self.save(update_fields=['file_size'])

        return self.file_size

    def _set_file_hash(self, file_contents):
        self.file_hash = hashlib.sha1(file_contents).hexdigest()

    def get_file_hash(self):
        if self.file_hash == '':
            with self.open_file() as f:
                self._set_file_hash(f.read())

            self.save(update_fields=['file_hash'])

        return self.file_hash

    def get_upload_to(self, filename):
        folder_name = 'original_images'
        filename = self.file.field.storage.get_valid_name(filename)

        # do a unidecode in the filename and then replace non-ascii
        # characters in filename with _ , to sidestep issues with
        # filesystem encoding
        filename = "".join((i if ord(i) < 128 else '_')
                           for i in unidecode(filename))

        # Truncate filename so it fits in the 100 character limit
        # https://code.djangoproject.com/ticket/9893
        full_path = os.path.join(folder_name, filename)
        if len(full_path) >= 95:
            chars_to_trim = len(full_path) - 94
            prefix, extension = os.path.splitext(filename)
            filename = prefix[:-chars_to_trim] + extension
            full_path = os.path.join(folder_name, filename)

        return full_path

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtailimages:image_usage',
                       args=(self.id,))

    search_fields = CollectionMember.search_fields + [
        index.SearchField('title', partial_match=True, boost=10),
        index.AutocompleteField('title'),
        index.FilterField('title'),
        index.FilterField('uploaded_by_user'),
    ]

    def __str__(self):
        return self.title

    @contextmanager
    def open_file(self):
        # Open file if it is closed
        close_file = False
        try:
            image_file = self.file

            if self.file.closed:
                # Reopen the file
                if self.is_stored_locally():
                    self.file.open('rb')
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance. #1397
                    storage = self._meta.get_field('file').storage
                    image_file = storage.open(self.file.name, 'rb')

                close_file = True
        except IOError as e:
            # re-throw this as a SourceImageIOError so that calling
            # code can distinguish these from IOErrors elsewhere in
            # the process
            raise SourceImageIOError(str(e))

        # Seek to beginning
        image_file.seek(0)

        try:
            yield image_file
        finally:
            if close_file:
                image_file.close()

    @contextmanager
    def get_willow_image(self):
        with self.open_file() as image_file:
            yield WillowImage.open(image_file)

    def get_rect(self):
        return Rect(0, 0, self.width, self.height)

    def get_focal_point(self):
        if self.focal_point_x is not None and \
           self.focal_point_y is not None and \
           self.focal_point_width is not None and \
           self.focal_point_height is not None:
            return Rect.from_point(
                self.focal_point_x,
                self.focal_point_y,
                self.focal_point_width,
                self.focal_point_height,
            )

    def has_focal_point(self):
        return self.get_focal_point() is not None

    def set_focal_point(self, rect):
        if rect is not None:
            self.focal_point_x = rect.centroid_x
            self.focal_point_y = rect.centroid_y
            self.focal_point_width = rect.width
            self.focal_point_height = rect.height
        else:
            self.focal_point_x = None
            self.focal_point_y = None
            self.focal_point_width = None
            self.focal_point_height = None

    def get_suggested_focal_point(self):
        with self.get_willow_image() as willow:
            faces = willow.detect_faces()

            if faces:
                # Create a bounding box around all faces
                left = min(face[0] for face in faces)
                top = min(face[1] for face in faces)
                right = max(face[2] for face in faces)
                bottom = max(face[3] for face in faces)
                focal_point = Rect(left, top, right, bottom)
            else:
                features = willow.detect_features()
                if features:
                    # Create a bounding box around all features
                    left = min(feature[0] for feature in features)
                    top = min(feature[1] for feature in features)
                    right = max(feature[0] for feature in features)
                    bottom = max(feature[1] for feature in features)
                    focal_point = Rect(left, top, right, bottom)
                else:
                    return None

        # Add 20% to width and height and give it a minimum size
        x, y = focal_point.centroid
        width, height = focal_point.size

        width *= 1.20
        height *= 1.20

        width = max(width, 100)
        height = max(height, 100)

        return Rect.from_point(x, y, width, height)

    @classmethod
    def get_rendition_model(cls):
        """ Get the Rendition model for this Image model """
        return cls.renditions.rel.related_model

    def get_rendition(self, filter):
        if isinstance(filter, str):
            filter = Filter(spec=filter)

        cache_key = filter.get_cache_key(self)
        Rendition = self.get_rendition_model()

        try:
            rendition = self.renditions.get(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
            )
        except Rendition.DoesNotExist:
            # Generate the rendition image
            generated_image = filter.run(self, BytesIO())

            # Generate filename
            input_filename = os.path.basename(self.file.name)
            input_filename_without_extension, input_extension = \
                os.path.splitext(input_filename)

            # A mapping of image formats to extensions
            FORMAT_EXTENSIONS = {
                'jpeg': '.jpg',
                'png': '.png',
                'gif': '.gif',
            }

            output_extension = filter.spec.replace('|', '.') + \
                FORMAT_EXTENSIONS[generated_image.format_name]
            if cache_key:
                output_extension = cache_key + '.' + output_extension

            # Truncate filename to prevent it going over 60 chars
            output_filename_without_extension = \
                input_filename_without_extension[:(59 - len(output_extension))]
            output_filename = output_filename_without_extension + '.' + \
                output_extension

            rendition, created = self.renditions.get_or_create(
                filter_spec=filter.spec,
                focal_point_key=cache_key,
                defaults={'file': File(generated_image.f,
                                       name=output_filename)}
            )

        return rendition

    def is_portrait(self):
        return (self.width < self.height)

    def is_landscape(self):
        return (self.height < self.width)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def default_alt_text(self):
        # by default the alt text field (used in rich text insertion)
        # is populated from the title. Subclasses might provide a
        # separate alt field, and override this
        return self.title

    def is_editable_by_user(self, user):
        from wagtail.images.permissions import permission_policy
        return permission_policy.user_has_permission_for_instance(
            user, 'change', self)

    class Meta:
        abstract = True
