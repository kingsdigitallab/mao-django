import json
from random import shuffle

from django import forms
from django.core.validators import RegexValidator
from django.db import models
from django.shortcuts import render
from django.urls import reverse

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel
)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.documents.models import Document
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.search.query import MatchAll
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from .blocks import BiographyStreamBlock, FootnotesStreamBlock


DATE_REGEX = r'^(-)?\d{4}(-[01][0-9](-[0-3][0-9])?)?$'
DATE_MESSAGE = 'Enter a valid date (YYYY, YYYY-MM, or YYYY-MM-DD)'


def get_map_markers(places):
    markers = []
    for idx, place in enumerate(places):
        popup = '<h4>{}</h4><h5>{}</h5>'.format(
            place.title, place.address, place.description)
        markers.append({'latlng': [place.latitude, place.longitude],
                        'popup': popup,
                        'title': 'map-marker-{}'.format(idx + 1)})
    if not markers:
        return ''
    return json.dumps(markers)


@register_snippet
class Event(models.Model):

    title = models.CharField(max_length=150)
    date_start = models.CharField(
        max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    date_end = models.CharField(
        blank=True, max_length=11,
        validators=[RegexValidator(regex=DATE_REGEX, message=DATE_MESSAGE)])
    description = RichTextField(blank=True)

    def __str__(self):
        return self.title

    def convert_date(self, date):
        """Returns `date` as a dictionary keyed by "year", "month", and
        "day". The date must be an ISO date format string, specifying
        a year, and optionally a month and day.

        """
        data = {'year': int(date[:4])}
        if len(date) > 4:
            data['month'] = int(date[5:7])
        if len(date) > 7:
            data['day'] = int(date[8:10])
        return data

    def get_event_data(self):
        event_data = {}
        event_data['start_date'] = self.convert_date(self.date_start)
        if self.date_end:
            event_data['end_date'] = self.convert_date(self.date_end)
        event_data['text'] = {
            'headline': self.title,
            'text': self.description
        }
        return event_data


@register_snippet
class Place(models.Model):

    title = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=100)
    description = RichTextField()

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
    description = RichTextField(blank=True,
                                help_text='Description of whole source')

    content_panels = Page.content_panels + [
        FieldPanel('source_type'),
        FieldPanel('description'),
        InlinePanel('pdfs', label='PDFs'),
        InlinePanel('images', label='images'),
        InlinePanel('texts', label='texts'),
        InlinePanel('urls', label='external resources (audio/video)'),
    ]

    subpage_types = []

    def resources(self):
        """Returns a QuerySet of all resources of the type specified for this
        source."""
        source_type = self.source_type
        if source_type == 'image':
            return self.images.all()
        elif source_type == 'pdf':
            return self.pdfs.all()
        elif source_type == 'text':
            return self.texts.all()
        else:
            return self.urls.all()


class Resource(Orderable):

    title = models.TextField()
    date = models.CharField(blank=True, max_length=20)
    creator = models.TextField(blank=True)
    publisher = models.TextField(blank=True)
    rights = models.TextField(blank=True)
    description = RichTextField(blank=True)

    class Meta:
        abstract = True
        ordering = ['sort_order']

    panels = [
        FieldPanel('title'),
        FieldPanel('creator'),
        FieldPanel('publisher'),
        FieldPanel('date'),
        FieldPanel('rights'),
        FieldPanel('description'),
    ]


class ImageResource(Resource):

    source = ParentalKey(SourcePage, related_name='images')
    image = models.OneToOneField(Image, on_delete=models.CASCADE,
                                 related_name='resource')

    panels = Resource.panels + [
        ImageChooserPanel('image'),
    ]


class PDFResource(Resource):

    source = ParentalKey(SourcePage, related_name='pdfs')
    document = models.ForeignKey(Document, on_delete=models.PROTECT,
                                 related_name='resources')
    preview_image = models.ForeignKey(Image, on_delete=models.PROTECT,
                                      related_name='pdfs')

    panels = Resource.panels + [
        DocumentChooserPanel('document'),
        ImageChooserPanel('preview_image'),
    ]


class TextResource(Resource):

    source = ParentalKey(SourcePage, related_name='texts')
    text = RichTextField()

    panels = Resource.panels + [
        FieldPanel('text'),
    ]


class URLResource(Resource):

    source = ParentalKey(SourcePage, related_name='urls')
    source_url = models.URLField(blank=True, verbose_name='URL')

    panels = Resource.panels + [
        FieldPanel('source_url'),
    ]


class ObjectBiographyPage(Page):

    byline = models.CharField(max_length=100)
    summary = models.TextField()
    biography = StreamField(BiographyStreamBlock())
    footnotes = StreamField(FootnotesStreamBlock(required=False), blank=True)
    further_reading = RichTextField(blank=True)
    featured_image = models.ForeignKey(
        Image, blank=True, on_delete=models.PROTECT, null=True,
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
        ImageChooserPanel('featured_image'),
        FieldPanel('related_objects', widget=forms.CheckboxSelectMultiple),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('biography'),
        index.SearchField('summary'),
        index.SearchField('footnotes'),
        index.RelatedFields('sources', [
            index.SearchField('title'),
            index.SearchField('description'),
        ]),
        # index.FilterField('name'),
        index.FilterField('tags'),
    ]

    subpage_types = []

    def serve(self, request):
        places = Place.objects.filter(biographies__biography=self)
        has_events = self.events.count() > 0
        context = {
            'has_events': has_events,
            'home': self.get_ancestors()[1],
            'map_markers': get_map_markers(places),
            'page': self,
            'places': places,
            'timeline_url': reverse('biography-timeline', args=[self.id]),
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


class ObjectBiographiesPage(Page):

    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    max_count = 1

    subpage_types = [ObjectBiographyPage]


class ProjectPage(Page):

    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    subpage_types = ['mao_era.ProjectPage']


class SourcesPage(Page):

    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    max_count = 1

    subpage_types = [SourcePage]


class MapPage(Page):

    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    max_count = 1

    def serve(self, request):
        biography_ids = ObjectBiographyPage.objects.live().values_list(
            'id', flat=True)
        places = Place.objects.filter(
            biographies__biography__in=biography_ids).distinct()
        context = {
            'map_markers': get_map_markers(places),
            'page': self,
            'places': places,
        }
        return render(request, self.template, context)


class TimelinePage(Page):

    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    max_count = 1

    def serve(self, request):
        context = {
            'page': self,
            'timeline_url': reverse('full-timeline'),
        }
        return render(request, self.template, context)


class HomePage(Page):

    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]

    max_count = 1

    subpage_types = [
        MapPage, ObjectBiographiesPage, ProjectPage, SourcesPage, TimelinePage, ObjectBiographyPage
    ]

    def serve(self, request):
        query_dict = request.GET.copy()
        # Filter by tags.
        tags = query_dict.getlist('tag')
        biographies = self._filter_biographies_by_tags(tags)
        # Search.
        query = query_dict.get('q', '')
        search_results = self._search_biographies(biographies, query)
        # Facets.
        facets = self._get_facets(search_results, tags, query_dict)
        randomised_biographies = list(search_results)
        shuffle(randomised_biographies)
        context = {
            'biographies': randomised_biographies,
            'facets': facets,
            'page': self,
            'q': query,
            'tabs': query_dict.get('tabs', 'grid'),
        }
        return render(request, self.template, context)

    def _filter_biographies_by_tags(self, tags):
        """Returns a QuerySet of ObjectBiographyPages filtered by `tags`."""
        biographies = ObjectBiographyPage.objects.live()
        for tag in tags:
            biographies = biographies.filter(tags__name=tag)
        # You might think that the following two lines are pointless
        # database churn, but in fact omitting them causes the
        # selection of a tag to mean only that tag is ever retrieved
        # when faceting.
        ids = biographies.values('id')
        biographies = ObjectBiographyPage.objects.filter(id__in=ids)
        return biographies

    def _get_facets(self, search_results, tags, query_dict):
        """Returns a dictionary of facets applicable to `search_results`.

        Each facet includes its name, its count, and the querystring
        to un/apply it.

        """
        facets = {}
        # Trying to facet on empty search results generates an
        # exception. Helpful.
        if search_results:
            raw_facets = search_results.facet('tags')
            facets = []
            for (tag_id, count) in raw_facets.items():
                try:
                    tag_name = str(Tag.objects.get(id=tag_id))
                except Tag.DoesNotExist:
                    continue
                link, is_apply = self._get_tag_querystring(
                    tags, tag_name, query_dict)
                facets.append({'name': tag_name, 'count': count, 'link': link,
                               'is_apply': is_apply})
        return facets

    def _get_tag_querystring(self, tags, tag_name, query_dict):
        """Returns the un/apply querystring for tag_name, and whether it is
        for applying."""
        qd = query_dict.copy()
        if tag_name in tags:
            # Create a querystring for unapplying the facet.
            new_tags = tags.copy()
            new_tags.remove(tag_name)
            is_apply = False
        else:
            # Create a querystring for applying the facet.
            new_tags = tags + [tag_name]
            is_apply = True
        qd.setlist('tag', new_tags)
        return qd.urlencode(), is_apply

    def _search_biographies(self, biographies, query):
        """Returns those `biographies` matched by `query`."""
        if not query:
            query = MatchAll()
        return biographies.search(query)
