import coreschema
from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    CharField,
    DateTimeField,
    ListField,
    ModelSerializer,
    PrimaryKeyRelatedField,
)

from teams.views import Team, TeamListSerializer
from users.serializers.players import PlayerListSerializer

from ..models import Game, Location, RsvpStatus
from .locations import LocationSerializer
from .rsvps import *

__all__ = [
    'GameCreateSerializer',
    'GameDetailsSerializer',
    'GameListSerializer',
]


class GameListSerializer(ModelSerializer):
    """
    Simplified game representation for use in list APIs (read only)
    """
    teams = TeamListSerializer(many=True)
    location = LocationSerializer()

    class Meta:
        model = Game
        fields = 'id', 'teams', 'datetime', 'location', 'name'
        read_only_fields = fields

    def to_representation(self, game):
        data = super().to_representation(game)

        if getattr(game, 'rsvp', None) is not None:
            data['rsvp'] = game.rsvp
            data['rsvp_id'] = game.rsvp_id

        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse('game-detail', (game.id, ),
                                  request=request)
        return data


class GameCreateSerializer(ModelSerializer):
    """
    Special format for game creation. Primarily due to providing a way to
    add multiple games at once (series of games) that are only differ by
    the datetime
    """

    teams = PrimaryKeyRelatedField(
        many=True,
        required=False,
        queryset=Team.objects.all(),
    )
    location = LocationSerializer(validators=[])
    datetime = DateTimeField(required=False)
    datetimes = ListField(
        child=DateTimeField(),
        help_text='extra datetimes, will automatically create more games',
        required=False,
        write_only=True,
    )
    name = CharField(help_text='game name', required=False)

    class Meta:
        model = Game
        fields = 'id', 'teams', 'name', 'datetime', 'datetimes', 'location',

    def is_valid(self, *args, **kwargs):
        # Work around an issue with the browsable api where empty input
        # value becomes [''] for a list field
        if self.initial_data.get('datetimes', None) == '':
            self.initial_data._mutable = True
            self.initial_data.pop('datetimes')
        return super().is_valid(*args, **kwargs)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)

        self_fields = self.fields
        request = self.context.get('request', None)

        if request:
            teams = fields['teams'].child_relation
            teams.queryset = request.user.managed_teams

        return fields

    def to_representation(self, obj):
        data = super().to_representation(obj)

        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse('game-detail', (obj.id, ),
                                  request=request)
        return data

    @atomic
    def create(self, validated_data):
        location_data = validated_data['location']
        teams = validated_data.get('teams', [])
        request = self.context.get('request', None)
        datetimes = []

        if 'datetime' in validated_data:
            datetimes.append(validated_data['datetime'])
        if 'datetimes' in validated_data:
            datetimes += validated_data['datetimes']

        # FIXME: move validation logic to .is_valid()
        if not datetimes:
            raise ValidationError(
                'Must include at least one of the following fields: '
                'datetime, datetimes'
            )
        if len(teams) > 2:
            raise ValidationError('Please pick up to 2 teams')

        location_obj, _ = Location.objects.get_or_create(
            name=location_data['name'],
            address=location_data['address'],
        )

        games = []
        game_name = validated_data.get('name', '')
        for i, dt in enumerate(datetimes):
            name_suffix = f' ({i + 1})' if i > 0 and game_name else ''
            game = Game.objects.create(
                datetime=dt,
                location=location_obj,
                organizer=request.user,
                name=game_name + name_suffix,
            )
            game.teams.add(*teams)

            for i, team in enumerate(teams):
                for player in team.players.filter(role__gt=0):
                    rsvp, _ = RsvpStatus.objects.get_or_create(
                        game=game,
                        player=player,
                    )
                    rsvp.team = i
                    if player.id == request.user.id:
                        rsvp.status = RsvpStatus.GOING
                    else:
                        rsvp.status = RsvpStatus.INVITED
                    rsvp.save()

            if not teams:
                RsvpStatus.objects.create(
                    game=game,
                    player=request.user,
                    status=RsvpStatus.GOING,
                )
            games.append(game)

        return games[0]


class GameDetailsSerializer(ModelSerializer):
    """
    Detailed game representation
    """
    location = LocationSerializer(read_only=True)
    organizer = PlayerListSerializer(read_only=True)
    players = RsvpSerializer(source='rsvps', many=True, read_only=True)
    teams = TeamListSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = 'players', 'organizer', 'teams'
