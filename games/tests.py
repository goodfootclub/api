from datetime import datetime, timedelta

import pytest
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from main.tests import mixer, client
from teams.models import Role
from .models import Game, Location, RsvpStatus

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


def test_my_games(client):
    mixer.cycle(5).blend(
        'games.RsvpStatus',
        status=RsvpStatus.GOING,
        player=client.user
    )

    url = reverse('game-my')
    res = client.get(url)

    assert res.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert res.data['count'] == 5, 'User should have 5 games'


def test_game_invites(client):
    mixer.cycle(5).blend(
        'games.RsvpStatus',
        status=RsvpStatus.INVITED,
        player=client.user
    )

    url = reverse('game-invites')
    res = client.get(url)

    assert res.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert res.data['count'] == 5, 'User should have 5 invites'


def test_pickup_games(client):
    mixer.cycle(5).blend('games.Game')

    url = reverse('game-list')
    res = client.get(url)

    assert res.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert res.data['count'] == 5, 'Should be 5 games'


def test_game_in_the_past(client):
    game = mixer.blend('games.Game', datetime=datetime.utcnow() - timedelta(1))

    list_url = reverse('game-list')
    res = client.get(list_url)

    assert res.status_code == status.HTTP_200_OK, 'Request should succeed'
    assert res.data['results'] == [], 'The game should not be in the results'

    res = client.get(list_url, {'all': 'true'})

    assert res.data['count'] == 1, 'Unless `all` param is supplied'

    retrive_url = reverse('game-detail', (game.id, ))
    res = client.get(retrive_url)

    assert res.status_code == status.HTTP_200_OK, \
        'Game should be retrievable without additional parameters'

    mixer.blend(
        'games.RsvpStatus',
        game=game,
        player=client.user,
        status=RsvpStatus.GOING
    )
    my_url = reverse('game-my')
    res = client.get(my_url, {'all': 'true'})
    assert res.data['count'] == 1, '`all` param should work for my games'


def test_game_edit_permission(client):
    users_game = mixer.blend('games.Game', organizer=client.user)
    other_game = mixer.blend('games.Game')

    users_game_url = reverse('game-detail', (users_game.id, ))
    other_game_url = reverse('game-detail', (other_game.id, ))

    res = client.patch(users_game_url, {'description': 'test'})
    assert res.status_code == status.HTTP_200_OK, \
        'User should be able to edit his game'

    res = client.patch(other_game_url, {'description': 'test'})
    assert res.status_code == status.HTTP_403_FORBIDDEN, \
        'User should not be able to edit other users games'


def test_game_organizer_can_invite():
    organizer = mixer.blend('users.User')
    players = mixer.cycle(6).blend('users.User')
    pickup_game = mixer.blend('games.Game', organizer=organizer)
    other_game = mixer.blend('games.Game')

    pickup_url = reverse('rsvp-list', (pickup_game.id, ))
    other_url = reverse('rsvp-list', (other_game.id, ))

    client = APIClient()
    client.force_authenticate(organizer)

    res = client.post(pickup_url, {
        'id': players[0].id,
        'rsvp': RsvpStatus.INVITED,
    })

    assert res.status_code == status.HTTP_201_CREATED, \
        'Organizer can invite a player to his game'
    assert players[0].rsvps.count() == 1
    assert players[0].rsvps.get().status == RsvpStatus.INVITED

    for i, (rsvp, _) in enumerate(RsvpStatus.RSVP_CHOICES):
        if rsvp == RsvpStatus.INVITED:
            continue

        res = client.post(pickup_url, {'id': players[i + 1].id, 'rsvp': rsvp})
        assert res.status_code == status.HTTP_403_FORBIDDEN, \
            'Organizer can not do anything other than inviting'

    for i, (rsvp, _) in enumerate(RsvpStatus.RSVP_CHOICES):
        res = client.post(other_url, {'id': players[i + 1].id, 'rsvp': rsvp})
        assert res.status_code == status.HTTP_403_FORBIDDEN, \
            'Organizer can not do anything in another game'
