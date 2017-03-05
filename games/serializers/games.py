
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    ListField,
    DateTimeField,
)

from teams.views import TeamListSerializer, TeamDetailsSerializer
from users.serializers.players import PlayerListSerializer
from .locations import LocationSerializer
from .rsvps import *
from ..models import Game, Location, RsvpStatus


__all__ = [
    'GameCreateSerializer',
    'GameDetailsSerializer',
    'GameListCreateSerializer',
    'GameListSerializer',
    'GameSerializer',
    'GameSerializer_',
]


class GameCreateSerializer(ModelSerializer):
    location = LocationSerializer(validators=[])
    datetime = DateTimeField(required=False)
    datetimes = ListField(
        child=DateTimeField(),
        help_text='(optional) extra datetimes, will automatically create '
                  'more games',
        required=False,
        write_only=True,
    )

    class Meta:
        model = Game
        fields = 'id', 'teams', 'datetime', 'datetimes', 'location'

    @atomic
    def create(self, validated_data):
        location_data = validated_data['location']
        request = self.context.get('request', None)
        datetimes = []

        if 'datetime' in validated_data:
            datetimes.append(validated_data['datetime'])
        if 'datetimes' in validated_data:
            datetimes += validated_data['datetimes']
        if not datetimes:
            # FIXME: move logic to .is_valid()
            raise ValidationError(
                'Must include at least one of the following fields: '
                'datetime, datetimes'
            )

        try:
            location_obj = Location.objects.get(
                name=location_data['name'],
                address=location_data['address'],
            )
        except Location.DoesNotExist:
            location_obj = Location.objects.create(
                name=location_data['name'],
                address=location_data['address'],
            )

        # FIXME: do bulk creates yo!
        games = []
        for dt in datetimes:
            game = Game.objects.create(
                datetime=dt,
                location=location_obj,
                organizer=request.user,
            )
            game.teams.add(*validated_data['teams'])

            RsvpStatus.objects.create(
                game=game,
                player=request.user,
                status=RsvpStatus.GOING,
            )
            games.append(game)

        return games[0]


class GameSerializer_(ModelSerializer):
    """Simple Game representation for polling and subsequent requests

    Fields:

     * id (Int) - read only, game id
     * datetime (ISO Datetime String) - date & time of a game (in UTC)
     * description (String) - any notes
     * duration (Int) - game duration in minutes
     * location (Int|Object) - id of Location or an object with name
        and address
     * organizer (Int) - read only, user id of the creator of the game
     * teams (Int[]) - team ids

    ## Example:

        {
            "id": 101,
            "datetime": "2017-01-20T02:52:00Z",
            "description": null,
            "duration": null,
            "location": 8,
            "organizer": 101,
            "teams": []
        }
    """
    class Meta:
        model = Game
        fields = (
            'id',
            'datetime',
            'description',
            'duration',
            'location',
            'organizer',
            'teams'
        )
        read_only_fields = 'organizer',

    def create(self, validated_data):
        location_data = validated_data['location']

        # TODO: test/improve Exception handling
        if isinstance(location_data, int):
            location_obj = super().create(validated_data)
        else:
            location_obj = Location.objects.get_or_create(
                name=location_data['name'],
                address=location_data['address'],
            )

        request = self.context.get('request', None)

        validated_data.update({
            'location': location_obj,
            'organizer': request.user,
        })

        game = Game.objects.create(**validated_data)

        RsvpStatus.objects.create(
            game=game,
            status=RsvpStatus.GOING,
            player=request.user,
        )

        return game


class GameListSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = 'id', 'teams', 'datetime', 'location'


class GameListCreateSerializer(ModelSerializer):
    teams = TeamListSerializer(many=True)
    location = LocationSerializer()

    class Meta:
        model = Game
        fields = 'id', 'teams', 'datetime', 'location'

    def to_representation(self, obj):
        data = super().to_representation(obj)

        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse('game-detail', (obj.id, ),
                                  request=request)
        return data

    # def to_internal_value(self, data):

    #     teams = data.pop('teams', [])
    #     value = super().to_internal_value(data)

    #     value['teams'] = []
    #     for team in teams:
    #         if team is None:
    #             continue
    #         if not isinstance(team, int):
    #             raise ValidationError
    #         team_obj = Team.objects.get(team)

    #     return value


class GameSerializer(ModelSerializer):

    players = RsvpListCreateSerializer(source='rsvps', many=True)

    class Meta:
        model = Game

    def to_internal_value(self, data):
        # Rsvps are managed with a separate view
        data.pop('players', None)
        return data


class GameDetailsSerializer(GameSerializer):

    players = RsvpDetailsSerializer(source='rsvps', many=True)
    organizer = PlayerListSerializer()
    teams = TeamDetailsSerializer(many=True)
    location = LocationSerializer()
