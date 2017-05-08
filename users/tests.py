import pytest
from main.tests import mixer
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_user_creation():
    user = mixer.blend('users.User', username='John')
    assert user.id is not None, 'User should exist in the database'
    assert user.username == 'John', 'User should have a username'


def test_current_user_view():
    user = mixer.blend('users.User')
    client = APIClient()
    client.force_authenticate(user=user)

    res = client.get(reverse('current-user'))

    assert res.status_code == status.HTTP_200_OK, \
        'Current user request should succeed when user is authenticated'

    assert res.data['id'] == user.id, \
        'users/me should return data info about the logged in user'


def test_user_has_game_invites():
    user = mixer.blend('users.User')
    future = mixer.faker.date_time_between(start_date='now')
    location = mixer.blend('games.Location')
    game = mixer.blend('games.Game', datetime=future)

    client = APIClient()
    client.force_authenticate(user=user)

    res = client.get(reverse('current-user'))

    assert res.status_code == status.HTTP_200_OK, \
        'Current user request should succeed when user is authenticated'

    assert res.data['id'] == user.id, \
        'users/me should return data info about the logged in user'
