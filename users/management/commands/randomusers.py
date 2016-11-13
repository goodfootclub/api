"""Ensure that there are randomly generated users in the system.

Data is acquired using https://randomuser.me ♥

These users have special prefix in their usernames to tell them apart from
other accounts you may have and in the system, in case there is a need to
remove or update the data
"""
import requests
from django.core.management.base import BaseCommand, CommandError

from users.models import User

# Desired number of randomly generated users in the system
DEFAULT_COUNT = 100

# A way to tell which users were randomly generated
USERNAME_PREFIX = '_rndgnd'
VERSION = 'v001'  # Change this when you update the command
VERSIONED_PREFIX = USERNAME_PREFIX + VERSION

# Refer to the https://randomuser.me/documentation for the full list of
# parameters available for their api
API_URL = 'https://randomuser.me/api/?results={count}&seed=gfc&nat=us'


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            dest='count',
            type=int,
            default=DEFAULT_COUNT,
            help='Number of random users desired in the system '
                 '(Default {}).'.format(DEFAULT_COUNT),
        )

    def handle(self, *args, **options):
        count = options['count']
        if count > 5000:
            raise CommandError('Can\'t be more than 5000 users')

        users = User.objects.filter(username__startswith=USERNAME_PREFIX)
        if (
            users.count() >= count > 0 and
            users.first().username.startswith(VERSIONED_PREFIX)
        ):
            self.stdout.write('Already enough users in the system')
            return

        deleted_count, _ = users.delete()
        if deleted_count:
            self.stdout.write('Deleted {} records'.format(deleted_count))
            if count == 0:
                return

        url = API_URL.format(count=options['count'])
        response = requests.get(url)
        data = response.json()

        User.objects.bulk_create(User(
            email=res['login']['password'],
            first_name=res['name']['first'],
            last_name=res['name']['last'],
            password=res['login']['password'],
            username=VERSIONED_PREFIX + res['login']['username'],
        ) for res in data['results'])

        self.stdout.write(self.style.SUCCESS(
            'Successfully added "{}" random users'.format(options['count'])
        ))
