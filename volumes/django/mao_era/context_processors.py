from django.conf import settings


def django_settings(request):
    return {'GA_ID': settings.GA_ID}
