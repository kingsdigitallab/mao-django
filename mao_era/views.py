import json

from django.http import HttpResponse

from .models import Event, ObjectBiographyPage


def bio_timeline(request, bio_id):
    """Returns the timeline data for the ObjectBiography with `bio_id` in
    JSON format."""
    events = Event.objects.filter(biographies__biography__id=bio_id)
    return timeline(events)


def full_timeline(request):
    biographies = ObjectBiographyPage.objects.live()
    events = Event.objects.filter(biographies__biography__id__in=biographies)
    return timeline(events)


def timeline(events):
    data = {'events': []}
    for event in events:
        data['events'].append(event.get_event_data())
    return HttpResponse(json.dumps(data), content_type='application/json')
