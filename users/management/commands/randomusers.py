"""Ensure that there are randomly generated users in the system.

Data is acquired using https://randomuser.me ♥

These users have special prefix in their usernames to tell them apart from
other accounts you may have and in the system, in case there is a need to
remove or update the data
"""
from datetime import datetime

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand, CommandError

from users.models import User


BIOS = [
    'Test User. Please Ignore',
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit',
    'Fusce at odio velit. Phasellus magna eros, blandit in odio luctus, '
    'feugiat fermentum purus',
    'Donec volutpat in ante sed feugiat. Donec tempor dapibus justo vel '
    'dapibus',
    'Nunc pharetra, felis quis tincidunt fringilla, magna mi sagittis est, '
    'a volutpat lorem tortor vel ligula',
    'Nulla feugiat efficitur enim, quis luctus nisl laoreet sit amet',
    'Integer tempus pretium ante sit amet fringilla. Cras aliquet imperdiet',
    'Cras arcu urna, posuere eget laoreet eu, pellentesque nec quam',
    'Pellentesque viverra ante sed tortor pretium sollicitudin',
    'Morbi dignissim rutrum semper. Pellentesque ut neque vitae erat '
    'condimentum consectetur at ut nibh',
    'Nullam et blandit leo. Donec tempor bibendum ligula, et molestie quam'
    'vehicula eget',
    'Aenean mollis vehicula dignissim. Etiam accumsan massa quis ligula '
    'iaculis, sit amet aliquam nunc pharetra.',
]

# Desired number of randomly generated users in the system
DEFAULT_COUNT = 50

# A way to tell which users were randomly generated
USERNAME_PREFIX = '_rndgnd'
VERSION = 'v003'  # Change this when you update the command
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

        for i, res in enumerate(data['results']):
            dob = datetime.strptime(res['dob'].split()[0], "%Y-%m-%d").date()
            gender = {
                'male': User.MALE,
                'female': User.FEMALE
            }[res['gender']]
            phone = ''.join(c for c in res['phone'] if c in '1234567890')

            user = User(
                gender=gender,
                birthday=dob,
                phone=phone,
                profile_complete=True,
                bio=BIOS[i % len(BIOS)],
                email=res['login']['password'],
                first_name=res['name']['first'].capitalize(),
                last_name=res['name']['last'].capitalize(),
                username=VERSIONED_PREFIX + res['login']['username'],
            )

            user.set_password(res['login']['password'])

            img_url = res['picture']['large']
            img_filename = img_url.split('/')[-1]

            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(requests.get(img_url).content)
            img_temp.flush()

            user.img.save(img_filename, File(img_temp))
            user.save()

        self.stdout.write(self.style.SUCCESS(
            'Successfully added "{}" random users'.format(options['count'])
        ))
