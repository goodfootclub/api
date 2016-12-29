"""Ensure that there are randomly generated locations in the system
"""
from django.core.management.base import BaseCommand, CommandError

from games.models import Location


# Desired number of randomly generated locations in the system
NAMES = [
    'Granite Bay Park',
    'Granite Regional Park',
    'Grant Park, Midtown',
    'Hagginwood Park',
    'Kemp Park 2',
    'Kemp Park, Folsom',
    'Peterson Park, Lodi',
]

# A way to tell which locations were randomly generated
ADDR_PREFIX = 'Test place '
VERSION = 'v001'  # Change this when you update the command
VERSIONED_PREFIX = ADDR_PREFIX + VERSION


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        count = len(NAMES)

        locations = Location.objects.filter(address__startswith=ADDR_PREFIX)
        if (
            locations.count() >= count > 0 and
            locations.first().address.startswith(VERSIONED_PREFIX)
        ):
            self.stdout.write('Already enough locations in the system')
            return

        deleted_count, _ = locations.delete()
        if deleted_count:
            self.stdout.write('Deleted {} records'.format(deleted_count))
            if count == 0:
                return

        for i, name in enumerate(NAMES):
            Location(name=name, address=VERSIONED_PREFIX).save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully created "{}" random games'.format(count)
        ))
