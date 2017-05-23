import pytest
from main.tests import mixer
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from .models import Role, Team

pytestmark = pytest.mark.django_db


def test_team_create():
    user = mixer.blend('users.User')
    url = reverse('team-list')
    client = APIClient()

    res = client.post(url, {'name': 'Test team'})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, \
        'Unauthenticated user can not create teams'

    client.force_authenticate(user=user)

    res = client.post(url, {'name': 'Test team'})
    assert res.status_code == status.HTTP_201_CREATED, \
        'User can create a team'

    res = client.post(url, {})
    assert res.status_code == status.HTTP_400_BAD_REQUEST, \
        'Should not create a team without a name'


def test_team_retrieve():
    user = mixer.blend('users.User')
    client = APIClient()
    client.force_authenticate(user=user)

    team = mixer.blend('teams.Team')
    url = reverse('team-detail', (team.id, ))

    res = client.get(url)
    assert res.status_code == status.HTTP_200_OK, \
        'Should be able to retrieve team info'


def test_team_add_player():
    player = mixer.blend('users.User')
    team_manager = mixer.blend('users.User')
    team = mixer.blend('teams.Team', managers=[team_manager])

    team_url = reverse('team-detail', (team.id, ))
    team_players_url = reverse('team-role-list', (team.id, ))

    client = APIClient()
    client.force_authenticate(user=team_manager)

    res = client.post(team_players_url, {
        'id': player.id,
        'role': Role.INVITED,
    })
    assert res.status_code == status.HTTP_201_CREATED, \
        'Team manager can invite players to his teams'

    role_id = res.data['role_id']
    role_url = reverse('team-role-detail', (team.id, role_id))

    client.force_authenticate(user=player)
    res = client.put(role_url, {'role': Role.FIELD})
    assert res.status_code == status.HTTP_200_OK, \
        'Invited player can accept an invite'

    assert player in team.players.all(), 'Player should be in the team now'


def test_my_teams():
    user = mixer.blend('users.User')
    client = APIClient()
    client.force_authenticate(user=user)

    team = mixer.blend('teams.Team', managers=[user])
    url = reverse('team-managed')
    res = client.get(url)

    assert res.status_code == status.HTTP_200_OK, \
        'Should be able to retrieve managed teams'

    assert res.data['count'] == 1, \
        'Should be exactly one'


def test_team_creator_added_as_player():
    """
    User that creates a team should be added to that teams as a player
    automatically
    """
    user = mixer.blend('users.User')
    client = APIClient()
    client.force_authenticate(user=user)

    create_url = reverse('team-list')
    res = client.post(create_url, {'name': 'Test team'})

    team = Team.objects.get(id=res.data['id'])

    assert user in team.players.all(), 'Creator should be a player'

    user2 = mixer.blend('users.User')
    team.managers.add(user2)
    assert user2 not in team.players.all(), \
        'Any extra managers are not added automatically'


def test_team_permissions():
    pass
