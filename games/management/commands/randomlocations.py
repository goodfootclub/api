"""Ensure that there are randomly generated locations in the system
"""
from django.core.management.base import BaseCommand, CommandError

from games.models import Location


# (name, address) test data
LOCATIONS = [(
    'Granite Bay Park',
    'Granite bay park-6010 Douglas Blvd., Granite Bay, CA 95746'
), (
    'Granite Regional Park',
    'Granite Regional Park-Ramona and Power Inn Sacramento, CA 95812'
), (
    'Grant Park, Midtown',
    'Grant Park, Midtown-205 21st St, Sacramento, CA 95811'
), (
    'Hagginwood Park',
    'Hagginwood Park-3271 Marysville Blvd, Sacramento, CA 95815'
), (
    'Kemp Park 2',
    'Kemp Park-1322 Bundrick Dr Folsom, CA 95630'
), (
    'Kemp Park, Folsom',
    'Kemp Park-1322 Bundrick Dr Folsom, CA 95630'
), (
    'Peterson Park, Lodi',
    'Peterson Park-2715 W Elm St, Lodi, CA 95242'
)]

# A way to tell which locations were randomly generated
ADDR_PREFIX = 'Test place '
VERSION = 'v002'  # Change this when you update the command
VERSIONED_PREFIX = ADDR_PREFIX + VERSION + ', '


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        count = len(LOCATIONS)

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

        for i, (name, address) in enumerate(LOCATIONS):
            Location(name=name, address=VERSIONED_PREFIX + address).save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully created "{}" random games'.format(count)
        ))
