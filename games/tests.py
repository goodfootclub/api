from datetime import datetime, timedelta

import pytest
from mixer.backend.django import mixer
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from teams.models import Role
from .models import Game

pytestmark = pytest.mark.django_db


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
        'datetime': datetime.utcnow() + timedelta(24 * 60),
        'location': {
            'address': address,
            'name': location_name,
        },
        'teams': [team.id],
    })

    assert res.status_code == status.HTTP_201_CREATED, \
        'Team manager shoudl be able to create a game for his team'

    game = Game.objects.get(id=res.data['id'])

    assert player1 in game.players.all(), \
        'Player that was in the team should be automatically intited'

    # Invite another player to the team
    team_players_url = reverse('team-role-list', (team.id, ))
    res = client.post(team_players_url, {
        'id': player2.id,
        'role': Role.INVITED,
    })
    assert res.status_code == status.HTTP_201_CREATED, \
        'Team manager can invite players to his teams'

    # assert player2 in game.players.all(), \
    #     'Player joining a team should be invited to the future team games'
