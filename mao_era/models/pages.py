import json

from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.shortcuts import render

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.images.models import AbstractRendition
from wagtail.search.query import MatchAll
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from .blocks import BiographyStreamBlock, FootnotesStreamBlock
from .images import AbstractImage


DATE_REGEX = r'^(-)?\d{4}(-[01][0-9](-[0-3][0-9])?)?$'
DATE_MESSAGE = 'Enter a valid date (YYYY, YYYY-MM, or YYYY-MM-DD)'


@register_snippet
class Event(models.Model):

    title = models.CharField(max_length=50)
    date_start = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    date_end = models.CharField(
        blank=True, max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    description = RichTextField(blank=True)

    def __str__(self):
        return self.title


@register_snippet
class Place(models.Model):

    title = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title


class ObjectBiographyTag(TaggedItemBase):

    content_object = ParentalKey(
        'mao_era.ObjectBiographyPage', on_delete=models.CASCADE,
        related_name='tagged_items')


class SourcePage(Page):

    SOURCE_TYPE_CHOICES = (
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('text', 'Text'),
        ('video', 'Video'),
    )

    source_type = models.CharField(max_length=5, choices=SOURCE_TYPE_CHOICES)
    date = models.CharField(max_length=20)
    creator = models.TextField()
    publisher = models.TextField()
    rights = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('source_type'),
        FieldPanel('date'),
        FieldPanel('creator'),
        FieldPanel('publisher'),
        FieldPanel('rights'),
        InlinePanel('pdfs', label='PDFs'),
        InlinePanel('images', label='images'),
        InlinePanel('texts', label='texts'),
        InlinePanel('urls', label='external resources (audio/video)'),
    ]

    subpage_types = []


class SourceImage(AbstractImage, Orderable):

    # Wagtail will silently fail to show a RichTextField in the
    # editing image upload interface.
    source = ParentalKey(SourcePage, blank=True, null=True,
                         on_delete=models.CASCADE, related_name='images')

    admin_form_fields = (
        'title',
        'file',
        'collection',
        'focal_point_x',
        'focal_point_y',
        'focal_point_width',
        'focal_point_height',
        'source',
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('file'),
    ]


class SourceImageRendition(AbstractRendition):

    image = models.ForeignKey(SourceImage, on_delete=models.CASCADE,
                              related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )


class SourcePDF(Orderable):

    source = ParentalKey(SourcePage, related_name='pdfs')
    title = models.CharField(max_length=255)
    text_file = models.FileField()

    panels = [
        FieldPanel('title'),
        FieldPanel('text_file'),
    ]


class SourceText(Orderable):

    source = ParentalKey(SourcePage, related_name='texts')
    title = models.CharField(max_length=255)
    text = RichTextField()

    panels = [
        FieldPanel('title'),
        FieldPanel('text'),
    ]


class SourceURL(Orderable):

    source = ParentalKey(SourcePage, related_name='urls')
    title = models.CharField(max_length=255)
    source_url = models.URLField(blank=True, verbose_name='URL')

    panels = [
        FieldPanel('title'),
        FieldPanel('source_url'),
    ]


class ObjectBiographyPage(Page):

    byline = models.CharField(max_length=100)
    summary = models.TextField()
    biography = StreamField(BiographyStreamBlock())
    footnotes = StreamField(FootnotesStreamBlock(), blank=True)
    further_reading = RichTextField(blank=True)
    featured_image = models.ForeignKey(
        SourceImage, on_delete=models.PROTECT,
        related_name='featured_biographies')
    tags = ClusterTaggableManager(through=ObjectBiographyTag, blank=True)
    related_objects = ParentalManyToManyField('self', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('byline'),
        FieldPanel('summary'),
        FieldPanel('tags'),
        StreamFieldPanel('biography'),
        StreamFieldPanel('footnotes'),
        FieldPanel('further_reading'),
        InlinePanel('sources', label='sources'),
        InlinePanel('events', label='events'),
        InlinePanel('places', label='places'),
        FieldPanel('featured_image'),
        FieldPanel('related_objects', widget=forms.CheckboxSelectMultiple),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('biography'),
        index.SearchField('summary'),
        index.FilterField('name'),
        index.FilterField('tags'),
    ]

    subpage_types = []

    def get_map_markers(self):
        markers = []
        for place in Place.objects.filter(biographies__biography=self):
            popup = '<b>{}</b><br><i>{}</i><p>{}</p>'.format(
                place.title, place.address, place.description)
            markers.append({'latlng': [place.latitude, place.longitude],
                            'popup': popup})
        return json.dumps(markers)

    def serve(self, request):
        context = {
            'home': self.get_parent(),
            'map_markers': self.get_map_markers(),
            'page': self,
        }
        return render(request, self.template, context)


class ObjectBiographyEvent(models.Model):

    biography = ParentalKey(ObjectBiographyPage, on_delete=models.CASCADE,
                            related_name='events')
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name='biographies')

    panels = [
        SnippetChooserPanel('event')
    ]

    class Meta:
        unique_together = ('biography', 'event')


class ObjectBiographyPlace(models.Model):

    biography = ParentalKey(ObjectBiographyPage, on_delete=models.CASCADE,
                            related_name='places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE,
                              related_name='biographies')

    panels = [
        SnippetChooserPanel('place')
    ]

    class Meta:
        unique_together = ('biography', 'place')


class ObjectBiographySource(models.Model):

    biography = ParentalKey(ObjectBiographyPage, on_delete=models.CASCADE,
                            related_name='sources')
    source = ParentalKey(SourcePage, on_delete=models.CASCADE,
                         related_name='biographies')

    panels = [
        PageChooserPanel('source')
    ]

    class Meta:
        unique_together = ('biography', 'source')


class ProjectPage(Page):

    pass


class TimelinePage(Page):

    pass


class HomePage(Page):

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    subpage_types = [
        ObjectBiographyPage, ProjectPage, SourcePage, TimelinePage
    ]

    def serve(self, request):
        biographies = ObjectBiographyPage.objects.live()
        # Filter by tags.
        tags = request.GET.getlist('tag')
        if tags:
            query = None
            for tag in tags:
                if query is None:
                    query = models.Q(tags__name=tag)
                else:
                    query = query & models.Q(tags__name=tag)
            biographies = biographies.filter(query)
        # Search.
        querystring = request.GET.get('q', '')
        query = querystring
        if not query:
            query = MatchAll()
        results = biographies.search(query)
        # Facets.
        facets = {}
        # Trying to facet on empty search results generates an
        # exception. Helpful.
        if results:
            raw_facets = results.facet('tags')
            facets = []
            for (tag_id, count) in raw_facets.items():
                facets.append((str(Tag.objects.get(id=tag_id)), count))
        context = {
            'biographies': results,
            'facets': facets,
            'page': self,
            'q': querystring,
        }
        return render(request, self.template, context)
