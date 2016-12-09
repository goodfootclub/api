"""Social auth pipeline extension

Mechanism for getting extra info from Facebook Graph API

Check out https://python-social-auth.readthedocs.io/en/latest/pipeline.html
for details
"""
import logging
import pprint
from datetime import date

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

import requests


FB_API_URL = (
    "https://graph.facebook.com/v2.8/me"
    "?fields=timezone,gender,email,birthday,picture.width(640),cover"
    "&access_token={token}"
)

logger = logging.getLogger('app.users.pipeline')


def facebook_extra_details(backend, user, *args, **kwargs):
    """Populate user object with extra details available with Facebook API
    """
    logger.debug(pprint.pformat(kwargs))
    logger.debug(backend.name)

    if backend.name != 'facebook':
        return

    social = kwargs.get('social')
    if not social:
        return

    url = FB_API_URL.format(token=social.extra_data['access_token'])

    response = requests.get(url)
    data = response.json()

    logger.debug(pprint.pformat(data))

    if not user.email and 'email' in data:
        user.email = data['email']

    if 'gender' in data:
        user.gender = {
            'male': user.MALE,
            'female': user.FEMALE
        }[data['gender']]

    # TODO: Facebook API gives you users current UTC offset as a
    # "timezone" and getting an actual timezone from it is non-trivial
    # so setting it for later
    # if 'timezone' in data:
    #     user.timezone = data['timezone']

    if not user.birthday and 'birthday' in data:
        birthday = list(map(int, data['birthday'].split('/')))

        day = month = 1
        year = 1900

        # it's either MM/DD/YYYY or MM/DD or YYYY so:
        try:
            year = birthday[-1]
            month, day = birthday[0:2]
            month, day, year = birthday
        except ValueError:  # When there's not enough values to unpack
            pass

        user.birthday = date(year=year, month=month, day=day)

    # Getting profile and cover images
    # TODO: consider making a celery task for getting images
    # Since this is one time thing that happening after user signs up
    # we will fetch images in place for now

    if not user.img.name and 'picture' in data:
        img_url = data['picture']['data']['url']

        img_filename = img_url.split('/')[-1]
        img_filename = img_filename.split('?', 1)[0]

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(requests.get(img_url).content)
        img_temp.flush()

        user.img.save(img_filename, File(img_temp))

    if not user.cover.name and 'cover' in data:
        cover_url = data['cover']['source']

        cover_filename = cover_url.split('/')[-1]
        cover_filename = cover_filename.split('?', 1)[0]

        cover_temp = NamedTemporaryFile(delete=True)
        cover_temp.write(requests.get(cover_url).content)
        cover_temp.flush()

        user.cover.save(cover_filename, File(cover_temp))

    user.save()
