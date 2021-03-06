from datetime import datetime, timedelta
from itertools import chain, product

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


def test_rsvps_annotation():
    user = mixer.blend('users.User')
    game = mixer.blend('games.Game')
    RsvpStatus(player=user, game=game, status=RsvpStatus.GOING).save()
    RsvpStatus(player=mixer.blend('users.User'),
               game=game, status=RsvpStatus.GOING).save()

    annotated_game = Game.objects.with_rsvps(user)[0]
    assert annotated_game.rsvp == RsvpStatus.GOING

    client = APIClient()
    client.force_authenticate(user)

    res = client.get(reverse('game-list'))
    assert res.data['results'][0]['rsvp'] == RsvpStatus.GOING


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


def test_my_games():
    user = mixer.blend('users.User')
    mixer.cycle(5).blend(
        'games.RsvpStatus',
        status=RsvpStatus.GOING,
        player=user
    )

    client = APIClient()
    url = reverse('game-my')

    res = client.get(url)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED, \
        'Should not be accessable when not authenticated'

    client.force_authenticate(user=user)

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

    client.user.is_superuser = True
    client.user.save()

    res = client.patch(other_game_url, {'description': 'test'})
    assert res.status_code == status.HTTP_200_OK, \
        'Unless he is a superuser'


def test_rsvp_list(client):
    game = mixer.blend('games.Game')
    rsvps = mixer.cycle(5).blend('games.RsvpStatus', game=game)

    res = client.get(reverse('rsvp-list', (game.id, )))
    assert res.data['count'] == 5, 'Should have 5 rsvps'


def test_pickup_organizer_can_invite():
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


def test_can_join_pickup(client):
    pickup_games = mixer.cycle(5).blend('games.Game')

    for game, (rsvp, _) in zip(pickup_games, RsvpStatus.RSVP_CHOICES):
        res = client.post(
            reverse('rsvp-list', (game.id, )),
            {'id': client.user.id, 'rsvp': rsvp},
        )
        if rsvp > RsvpStatus.INVITED:
            assert res.status_code == status.HTTP_201_CREATED, \
                'User can join any pickup game he likes'
        else:
            assert res.status_code == status.HTTP_403_FORBIDDEN, \
                'Inviting yourself to a game you can join does not make sense'


def test_rsvp_create_validation(client):
    invalid_payloads = [
        {'id': client.user.id, 'rsvp': 'foo'},
        {'id': 'bar', 'rsvp': RsvpStatus.GOING},
        {'id': client.user.id},
        {'rsvp': RsvpStatus.GOING},  # this one in theory might be valid if
        {},                          # we implicitly use authenticated user
    ]
    pickup_games = mixer.cycle(len(invalid_payloads)).blend('games.Game')

    for payload, game in zip(invalid_payloads, pickup_games):
        res = client.post(reverse('rsvp-list', (game.id, )), payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST, \
            'Should rise validation error'


def test_rsvp_retreive(client):
    rsvp = mixer.blend('games.RsvpStatus')
    res = client.get(reverse('rsvp-detail', (rsvp.game.id, rsvp.id)))
    assert res.status_code == status.HTTP_200_OK, \
        'RsvpStatus can be accessed by any user'


def test_rsvp_update_by_user(client):
    RSVPS = [
        RsvpStatus.REQUESTED_TO_JOIN,
        RsvpStatus.INVITED,
        RsvpStatus.NOT_GOING,
        RsvpStatus.UNCERTAIN,
        RsvpStatus.GOING,
    ]

    def valid_transactions():
        return product(RSVPS[1:], RSVPS[2:])

    def invalid_transactions():
        return chain(
            product(RSVPS[2:], RSVPS[:2]),
            ((RsvpStatus.INVITED, RsvpStatus.REQUESTED_TO_JOIN), ),
        )

    pickup_rsvp = mixer.blend('games.RsvpStatus', player=client.user)
    rsvp_url = reverse('rsvp-detail', (pickup_rsvp.game.id, pickup_rsvp.id))

    for from_, to in valid_transactions():
        pickup_rsvp.status = from_
        pickup_rsvp.save()
        res = client.put(rsvp_url, {'rsvp': to})
        assert res.status_code == status.HTTP_200_OK, \
            'Player should be able to change his status'

    for from_, to in invalid_transactions():
        pickup_rsvp.status = from_
        pickup_rsvp.save()
        res = client.put(rsvp_url, {'rsvp': to})
        assert res.status_code == status.HTTP_403_FORBIDDEN, \
            'Player should not set his status to invited or uncertain'

    team = mixer.blend('teams.Team')
    game = mixer.blend('games.Game', teams=[team])
    team_rsvp = mixer.blend(
        'games.RsvpStatus',
        game=game,
        player=client.user,
        team=0,
    )
    team_rsvp_url = reverse('rsvp-detail', (team_rsvp.game.id, team_rsvp.id))

    for from_, to in valid_transactions():
        team_rsvp.status = from_
        team_rsvp.save()
        res = client.put(team_rsvp_url, {'rsvp': to})
        assert res.status_code == status.HTTP_200_OK, \
            'Player should be able to change his status'

    for from_, to in invalid_transactions():
        team_rsvp.status = from_
        team_rsvp.save()
        res = client.put(team_rsvp_url, {'rsvp': to})
        assert res.status_code == status.HTTP_403_FORBIDDEN, \
            'Player should not set his status to invited or uncertain'

    other_rsvp = mixer.blend('games.RsvpStatus')
    oher_url = reverse('rsvp-detail', (other_rsvp.game.id, other_rsvp.id))

    for from_, to in product(RSVPS, RSVPS):
        other_rsvp.status = from_
        other_rsvp.save()
        res = client.put(oher_url, {'rsvp': to})
        assert res.status_code == status.HTTP_403_FORBIDDEN, \
            'Should not be able to access any other players rsvp'


def test_rsvp_update_validation(client):
    invalid_payloads = [{'rsvp': 'foo'}, {}]

    rsvps = mixer.cycle(len(invalid_payloads)).blend(
        'games.RsvpStatus',
        player=client.user,
        status=RsvpStatus.INVITED
    )

    for payload, rsvp in zip(invalid_payloads, rsvps):
        rsvp_url = reverse('rsvp-detail', (rsvp.game.id, rsvp.id))
        res = client.put(rsvp_url, payload)
        assert res.status_code == status.HTTP_400_BAD_REQUEST, \
            'Player should be able to change his status'


def test_game_name(client):
    address = mixer.faker.address()
    location_name = ' '.join(address.split()[1:3])

    game_name = f'The game at {location_name}'

    res = client.post(reverse('game-list'), {
        'datetimes': [datetime.utcnow() + timedelta(i) for i in range(1, 5)],
        'location': {
            'address': address,
            'name': location_name,
        },
        'name': game_name,
    })

    game = Game.objects.get(id=res.data['id'])

    assert game.name == game_name, 'Should be able to create game with a name'

    games = Game.objects.filter(name__startswith=game_name)
    names = [item['name'] for item in games.values('name')]
    assert names == [
        game_name,
        game_name + ' (2)',
        game_name + ' (3)',
        game_name + ' (4)',
    ], 'Games created at once with a name should get a (n) suffix'

# TODO: team games
# TODO: delete
