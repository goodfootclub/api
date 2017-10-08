import pytest
from main.tests import mixer, client
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from games.models import RsvpStatus
from teams.models import Role

from .pipeline import facebook_extra_details

pytestmark = pytest.mark.django_db


def test_user_creation():
    user = mixer.blend('users.User', username='John')
    assert user.id is not None, 'User should exist in the database'
    assert user.username == 'John', 'User should have a username'


def test_current_user_view(client):
    res = client.get(reverse('current-user'))

    assert res.status_code == status.HTTP_200_OK, \
        'Current user request should succeed when user is authenticated'

    assert res.data['id'] == client.user.id, \
        'users/me should return data info about the logged in user'


def test_user_has_game_invites():
    user = mixer.blend('users.User')
    rsvp = mixer.blend(
        'games.RsvpStatus', player=user, status=RsvpStatus.INVITED
    )
    role = mixer.blend('teams.Role', player=user, status=Role.INVITED)

    client = APIClient()
    client.force_authenticate(user=user)

    res = client.get(reverse('current-user'))

    assert 'invites' in res.data, 'Sould have invites'

    assert res.data['invites'] == {'total': 2, 'teams': 1, 'games': 1}, \
        'Sould have two invites total, one for games and one for teams'


def test_facebook_pipeline(mocker):
    class MockResponse():
        def __init__(self, data):
            self.data = data

        def json(self):
            return self.data

    def get_mock(*args, **kwargs):
        return MockResponse({})

    requests_get = mocker.patch('requests.get', side_effect=get_mock)

    class NoImage:
        name = None

    class MockUser:
        email = 'mail@example.com'
        birthday = None
        img = NoImage()
        cover = NoImage()

        def save(self):
            pass

    class MockBackEnd:
        name = 'facebook'

    class MockSocial:
        extra_data = {'access_token': 'foobar'}

    facebook_extra_details(MockBackEnd(), MockUser(), social=MockSocial())


def test_email_blank_or_unique():
    alice = mixer.blend('users.User', email='alice@example.com')

    with pytest.raises(ValidationError):
        eve = mixer.blend('users.User', email='alice@example.com')

    mixer.cycle(2).blend('users.User', email='')


def test_account_delete():
    user = mixer.blend('users.User')
    user.set_password('1234')
    user.save()
    client = APIClient()
    client.login(username=user.username, password='1234')

    res = client.delete(reverse('current-user'))

    assert res.status_code == status.HTTP_204_NO_CONTENT, \
        'Current user should be able to delete his account'

    user.refresh_from_db()
    assert user.is_active is False, 'Must be a soft delete'

    res = client.get(reverse('current-user'))
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, \
        'Should log user out'


def test_passwodr_change():
    user = mixer.blend('users.User')
    user.set_password('1234')
    user.save()
    client = APIClient()
    client.login(username=user.username, password='1234')

    res = client.patch(reverse('current-user'), {'password': '4321'})

    assert res.status_code == status.HTTP_200_OK, \
        'Current user should be able to update his password'

    user.refresh_from_db()
    assert user.check_password('4321'), 'Should set new password'
