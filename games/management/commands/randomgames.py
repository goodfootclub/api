"""Ensure that there are randomly generated games in the system
"""
from random import choice, sample, randrange
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from users.models import User
from teams.models import Team
from games.models import Game, Location, RsvpStatus

from users.management.commands.randomusers import USERNAME_PREFIX
from .randomlocations import VERSIONED_PREFIX as LOCATIONS_PREFIX


# Desired number of randomly generated games in the system
DEFAULT_COUNT = 100

# A way to tell which games were randomly generated
DESC_PREFIX = '_rndgnd'
VERSION = 'v003'  # Change this when you update the command
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
        parser.add_argument(
            '-f', '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force (re)creationg of games',
        )

    def handle(self, *args, **options):
        count = options['count']
        force = options['force']

        games = Game.objects.filter(description__startswith=DESC_PREFIX)
        if (
            not force and games.count() >= count > 0 and
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
            game = Game.objects.create(
                datetime=now + timedelta(days=randrange(10)),
                description=VERSIONED_PREFIX,
                duration=choice([40, 45, 90]),
                location=choice(locations),
                organizer=choice(users),
            )

            RsvpStatus.objects.bulk_create([
                RsvpStatus(game=game, player=player, status=choice([1, 2]))
                for player in sample(users, choice([11 * 2, 8 * 2]))
            ])

        self.stdout.write(self.style.SUCCESS(
            'Successfully created "{}" random games'.format(options['count'])
        ))
