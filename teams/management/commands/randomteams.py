"""Ensure that there are randomly generated teams in the system
"""
from django.core.management.base import BaseCommand, CommandError

from teams.models import Team


NAMES = [
    'Kickballers',
    'Real Madrid',
    'Dortmund',
    'Manchester United',
    'Atlético Madrid',
    'Arsenal',
    'Milan',
    'Manchester city',
    'Chelsea',
    'Barcelona',
]

# Weighted types (60% male teams, female and coed are 20% each)
TYPES = [Team.MALE] * 3 + [Team.COED] + [Team.COED]

INFO_PREFIX = 'Test team'
VERSION = ' v001'
VERSIONED_PREFIX = INFO_PREFIX + VERSION


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        teams = Team.objects.filter(info__startswith=INFO_PREFIX)

        if (
            teams.count() >= len(NAMES) > 0 and
            teams.first().info.startswith(VERSIONED_PREFIX)
        ):
            self.stdout.write('Already enough teams in the system')
            return

        deleted_count, _ = teams.delete()
        if deleted_count:
            self.stdout.write('Deleted {} records'.format(deleted_count))
            if len(NAMES) == 0:
                return

        for i, name in enumerate(NAMES):
            Team(
                name=name,
                info=VERSIONED_PREFIX,
                type=TYPES[i % len(TYPES)],
            ).save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully added "{}" test teams'.format(len(NAMES))
        ))
