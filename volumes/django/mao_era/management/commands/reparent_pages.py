from django.core.management.base import BaseCommand
from django.db import transaction

from ...models import (HomePage, ObjectBiographiesPage, ObjectBiographyPage,
                       SourcePage, SourcesPage)


class Command(BaseCommand):

    help = 'Move all object biography pages and source pages under their ' \
        'respective index pages (creating the latter, if necessary).'

    def handle(self, *args, **options):
        with transaction.atomic():
            home = HomePage.objects.all()[0]
            try:
                biographies_page = ObjectBiographiesPage.objects.all()[0]
            except IndexError:
                biographies_page = ObjectBiographiesPage(
                    title='Object Biographies',
                    body='List of object biographies')
                home.add_child(instance=biographies_page)
            for biography_page in ObjectBiographyPage.objects.all():
                biography_page.move(biographies_page, 'last-child')

            try:
                sources_page = SourcesPage.objects.all()[0]
            except IndexError:
                sources_page = SourcesPage(title='Sources',
                                           body='List of sources')
                home.add_child(instance=sources_page)
            for source_page in SourcePage.objects.all():
                source_page.move(sources_page, 'last-child')
