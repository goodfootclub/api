import pytest
from main.tests import mixer
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from games.models import RsvpStatus
from teams.models import Role

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
    rsvp = mixer.blend(
        'games.RsvpStatus', player=user, status=RsvpStatus.INVITED
    )
    role = mixer.blend(
        'teams.Role', player=user, status=Role.INVITED
    )

    client = APIClient()
    client.force_authenticate(user=user)

    res = client.get(reverse('current-user'))

    assert 'invites' in res.data, 'Sould have invites'

    assert res.data['invites'] == {
        'total': 2,
        'teams': 1,
        'games': 1,
    }, 'Sould have two invites total, one game and one team invites'
