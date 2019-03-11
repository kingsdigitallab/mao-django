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
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import AbstractRendition
from wagtail.search.query import MatchAll
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from .blocks import BiographyStreamBlock
from .images import AbstractImage


DATE_REGEX = r'^(-)?\d{4}(-[01][0-9](-[0-3][0-9])?)?$'
DATE_MESSAGE = 'Enter a valid date (YYYY, YYYY-MM, or YYYY-MM-DD)'


@register_snippet
class Event(models.Model):

    name = models.CharField(max_length=50)
    date_start = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    date_end = models.CharField(
        blank=True, max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    note = RichTextField(blank=True)

    def __str__(self):
        return self.name


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
    copyright_statement = RichTextField()
    origin = RichTextField()
    text = RichTextField(blank=True)
    source_url = models.URLField(blank=True)
    text_file = models.FileField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('source_type'),
        FieldPanel('copyright_statement'),
        FieldPanel('origin'),
        FieldPanel('text'),
        FieldPanel('source_url'),
        FieldPanel('text_file'),
        InlinePanel('images', label='images'),
    ]

    subpage_types = []


class SourceImage(AbstractImage, Orderable):

    caption = RichTextField(blank=True)

    admin_form_fields = (
        'title',
        'caption',
        'file',
        'collection',
        'focal_point_x',
        'focal_point_y',
        'focal_point_width',
        'focal_point_height',
    )


class SourceImageRendition(AbstractRendition):

    image = models.ForeignKey(SourceImage, on_delete=models.CASCADE,
                              related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )


class SourcePageImage(models.Model):

    source = ParentalKey(SourcePage, on_delete=models.CASCADE,
                         related_name='images')
    image = models.ForeignKey(SourceImage, on_delete=models.CASCADE,
                              related_name='sources')

    panels = [
        ImageChooserPanel('image')
    ]

    class Meta:
        unique_together = ('source', 'image')


class ObjectBiographyPage(Page):

    byline = models.CharField(max_length=100)
    summary = models.TextField()
    biography = StreamField(BiographyStreamBlock())
    further_reading = RichTextField(blank=True)
    date_start = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    date_end = models.CharField(
        blank=True, max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    tags = ClusterTaggableManager(through=ObjectBiographyTag, blank=True)
    featured_image = models.ForeignKey(
        SourceImage, on_delete=models.PROTECT,
        related_name='featured_biographies')
    related_objects = ParentalManyToManyField('self', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('byline'),
        FieldPanel('summary'),
        StreamFieldPanel('biography'),
        FieldPanel('further_reading'),
        FieldPanel('date_start'),
        FieldPanel('date_end'),
        InlinePanel('sources', label='sources'),
        FieldPanel('featured_image'),
        InlinePanel('events', label='events'),
        FieldPanel('tags'),
        FieldPanel('related_objects', widget=forms.CheckboxSelectMultiple),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('biography'),
        index.SearchField('summary'),
        index.FilterField('name'),
        index.FilterField('tags'),
    ]

    subpage_types = []

    def serve(self, request):
        context = {
            'home': self.get_parent(),
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
