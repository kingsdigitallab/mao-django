import json

from django.contrib.staticfiles import finders
from django.http import HttpResponse, HttpResponseNotFound

import weasyprint

from .models import Event, ObjectBiographyPage, SourcePage


def bio_timeline(request, bio_id):
    """Returns the timeline data for the ObjectBiography with `bio_id` in
    JSON format."""
    events = Event.objects.filter(biographies__biography__id=bio_id)
    return timeline(events)


def biography_pdf(request, bio_id):
    try:
        bio = ObjectBiographyPage.objects.live().get(pk=bio_id)
    except ObjectBiographyPage.DoesNotExist:
        return HttpResponseNotFound()

    url = "http://django:8000{}".format(bio.url)

    html = weasyprint.HTML(url=url, base_url="http://nginx:8001")
    return _generate_pdf(html, bio.slug)


def full_timeline(request):
    biographies = ObjectBiographyPage.objects.live()
    events = Event.objects.filter(biographies__biography__id__in=biographies)
    return timeline(events)


def _generate_pdf(html, filename):
    css = weasyprint.CSS(
        filename=finders.find("scss/pdf.css"), base_url="http://nginx:8001"
    )
    doc = html.render(stylesheets=[css])
    response = HttpResponse(doc.write_pdf(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="{}.pdf"'.format(filename)
    return response


def source_pdf(request, source_id):
    try:
        source = SourcePage.objects.live().get(pk=source_id)
    except SourcePage.DoesNotExist:
        return HttpResponseNotFound()
    html = weasyprint.HTML(url=source.full_url)
    return _generate_pdf(html, source.slug)


def timeline(events):
    data = {"events": []}
    for event in events:
        data["events"].append(event.get_event_data())
    return HttpResponse(json.dumps(data), content_type="application/json")
