from datetime import datetime, timedelta

import pytest
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from main.tests import mixer
from teams.models import Role
from .models import Game, Location

pytestmark = pytest.mark.django_db


def test_game_model():
    game = mixer.blend('games.Game')
    assert str(game) != '', 'Should cover __str__'


def test_game_queryset_and_manager():
    old = mixer.blend('games.Game', datetime=datetime.utcnow() - timedelta(1))
    new = mixer.blend('games.Game', datetime=datetime.utcnow() + timedelta(1))

    future = Game.objects.future()
    assert new in future, 'New game should be in the `future` query'
    assert old not in future, 'Old game should not be in the `future` query'
    assert old in Game.objects.all(), 'Old game should be in all() still'


def test_location_model():
    location = mixer.blend('games.Location')
    assert isinstance(eval(str(location)), Location), 'Should cover __str__'

    with pytest.raises(IntegrityError):
        "Should not allow two instances with same name + address"
        mixer.cycle(2).blend('games.Location', name='foo', address='bar')


def test_game_create():
    player1, player2 = mixer.cycle(2).blend('users.User')
    team_manager = mixer.blend('users.User')
    team = mixer.blend('teams.Team', managers=[team_manager])

    player1_role = Role.objects.create(
        player=player1,
        team=team,
        role=Role.FIELD,
    )

    client = APIClient()
    client.force_authenticate(user=team_manager)

    games_url = reverse('game-list')
    address = mixer.faker.address()
    location_name = ' '.join(address.split()[1:3])
    res = client.post(games_url, {
        'datetime': datetime.utcnow() + timedelta(1),
        'location': {
            'address': address,
            'name': location_name,
        },
        'teams': [team.id],
    })

    assert res.status_code == status.HTTP_201_CREATED, \
        'Team manager should be able to create a game for his team'

    game = Game.objects.get(id=res.data['id'])

    assert player1 in game.players.all(), \
        'Player that was in the team should be automatically invited'

    # Invite another player to the team
    team_players_url = reverse('team-role-list', (team.id, ))
    res = client.post(team_players_url, {
        'id': player2.id,
        'role': Role.INVITED,
    })
    assert res.status_code == status.HTTP_201_CREATED, \
        'Team manager can invite players to his teams'

    assert player2 in game.players.all(), \
        'Player joining a team should be invited to the future team games'
