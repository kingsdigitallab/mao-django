import json

from django.http import HttpResponse

from .models import Event


def timeline(self, bio_id):
    """Returns the timeline data for the ObjectBiography with `bio_id` in
    JSON format."""
    data = {'events': []}
    for event in Event.objects.filter(biographies__biography__id=bio_id):
        event_data = {}
        event_data['start_date'] = event.convert_date(event.date_start)
        if event.date_end:
            event_data['end_date'] = event.convert_date(event.date_end)
        event_data['text'] = {
            'headline': event.title,
            'text': event.description
        }
        data['events'].append(event_data)
    return HttpResponse(json.dumps(data), content_type='application/json')
