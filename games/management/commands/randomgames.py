"""Ensure that there are randomly generated games in the system
"""
from random import choice

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from users.models import User
from teams.models import Team
from games.models import Game, Location

from users.management.commands.randomusers import USERNAME_PREFIX
from .randomlocations import VERSIONED_PREFIX as LOCATIONS_PREFIX


# Desired number of randomly generated games in the system
DEFAULT_COUNT = 100

# A way to tell which games were randomly generated
DESC_PREFIX = '_rndgnd'
VERSION = 'v002'  # Change this when you update the command
VERSIONED_PREFIX = DESC_PREFIX + VERSION


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            dest='count',
            type=int,
            default=DEFAULT_COUNT,
            help='Number of random games desired in the system '
                 '(Default {}).'.format(DEFAULT_COUNT),
        )

    def handle(self, *args, **options):
        count = options['count']

        games = Game.objects.filter(description__startswith=DESC_PREFIX)
        if (
            games.count() >= count > 0 and
            games.first().description.startswith(VERSIONED_PREFIX)
        ):
            self.stdout.write('Already enough games in the system')
            return

        deleted_count, _ = games.delete()
        if deleted_count:
            self.stdout.write('Deleted {} records'.format(deleted_count))
            if count == 0:
                return

        locations = list(Location.objects.filter(
            address__startswith=LOCATIONS_PREFIX
        ))
        users = list(User.objects.filter(
            username__startswith=USERNAME_PREFIX
        ))

        now = timezone.now()

        for i in range(count):
            Game(
                datetime=now,
                description=VERSIONED_PREFIX,
                duration=choice([40, 45, 90]),
                location=choice(locations),
                organizer=choice(users),
            ).save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully created "{}" random games'.format(options['count'])
        ))
