import logging
import pprint

from django.db import IntegrityError
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework import permissions
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ChoiceField,
    Field,
    HyperlinkedModelSerializer,
    IntegerField,
    ImageField,
    ModelSerializer,
    ReadOnlyField,
    Serializer,
)

from main.exceptions import RelationAlreadyExist
from teams.views import TeamListSerializer, TeamDetailsSerializer
from users.models import User
from users.views import PlayerListSerializer
from .models import Game, Location, RsvpStatus


logger = logging.getLogger('app.games.views')


class LocationSerializer(ModelSerializer):

    class Meta:
        model = Location


class RsvpSerializer(ModelSerializer):
    rsvp = ChoiceField(RsvpStatus.RSVP_CHOICES, source='status')
    rsvp_id = ReadOnlyField(source='id')

    class Meta:
        model = RsvpStatus
        fields = 'rsvp_id', 'rsvp',

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse(
                'game-rsvp',
                (self.context['view'].kwargs['game_id'], obj.id),
                request=request
            )
        return data

    def create(self, validated_data):
        if 'game_id' not in validated_data:
            validated_data.update(self.context['view'].kwargs)
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise RelationAlreadyExist(
                detail=e.args[0].split('DETAIL:  ')[1]
            )


class RsvpListCreateSerializer(RsvpSerializer):
    id = IntegerField(source='player_id')

    class Meta(RsvpSerializer.Meta):
        fields = 'id', 'rsvp_id', 'rsvp', 'team'


class RsvpDetailsSerializer(RsvpListCreateSerializer):

    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')
    img = ImageField(source='player.img', read_only=True)

    class Meta(RsvpListCreateSerializer.Meta):
        fields = RsvpListCreateSerializer.Meta.fields + (
            'first_name', 'last_name', 'img'
        )


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

    def create(self, validated_data):
        location_data = validated_data['location']

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

        request = self.context.get('request', None)

        game = Game.objects.create(
            location=location_obj,
            datetime=validated_data['datetime'],
            organizer=request.user,
        )

        RsvpStatus.objects.create(
            game=game,
            status=RsvpStatus.GOING,
            player=request.user,
        )

        return game


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


class GamesList(ListCreateAPIView):
    """Get a list of existing game events or make a new one"""
    serializer_class = GameListCreateSerializer
    queryset = Game.objects.all()


class GameDetails(RetrieveUpdateDestroyAPIView):
    """Check game details, change the info or delete it

    # Detailed view
    To get related models in a serialized form instead of ids
    [detailed view](?details) is available

    # Players
    Manage players rsvps with [/players](./players) method
    """
    queryset = Game.objects.all()
    lookup_url_kwarg = 'game_id'

    def get_serializer_class(self):
        if {'d', 'details'} & self.request.query_params.keys():
            return GameDetailsSerializer
        return GameSerializer


# TODO: move to a separate permissions module
class RsvpCreateUpdateDestroyPermission(permissions.BasePermission):
    """Ensure that the change is withing following options:
        - User joins pickup games and asks to join league games
        - Player changes status or leaves
        - Game organizer removes player from open games
        - Team manager can invite and remove players to/from league games
    """
    message = __doc__

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        if request.method == 'POST':
            data = request.data

            if not data:
                return True

            new_status = data.get('rsvp', None)
            new_team = data.get('team', None)
            new_player_id = data.get('id', None)

            # Only pickup games for now, No teams allowed yet
            if new_team and new_team != RsvpStatus.NO_TEAM:
                return False

            is_invite = new_status == RsvpStatus.INVITED
            is_request = new_status == RsvpStatus.REQUESTED_TO_JOIN
            is_rsvp = new_status is not None and new_status >= 0

            game = Game.objects.get(id=view.kwargs['game_id'])
            is_pickup_game = game.teams.count() == 0
            is_team_game = not is_pickup_game
            user = request.user
            user_is_organizer = user == game.organizer
            user_is_team_manager = False  # TODO:
            user_is_player = user.id == new_player_id

            return (
                (user_is_player and is_pickup_game and is_rsvp) or
                (user_is_player and is_team_game and is_request) or
                (user_is_organizer and is_pickup_game and is_invite) or
                (user_is_team_manager and is_team_game and is_invite)
            )

        return True

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        game = obj.game
        is_pickup_game = game.teams.count() == 0
        is_team_game = not is_pickup_game

        user = request.user
        user_is_organizer = user == game.organizer
        user_is_team_manager = False  # TODO:
        user_is_player = user == obj.player

        if request.method == 'DELETE':
            return (
                user_is_player or
                (user_is_organizer and is_pickup_game) or
                (user_is_team_manager and is_team_game)
            )

        data = request.data

        if not data:
            return True

        new_status = data.get('rsvp', None)
        old_status = obj.status
        is_rsvp = new_status is not None and new_status >= 0

        is_request_accept = ((
            (user_is_organizer and is_pickup_game) or
            (user_is_team_manager and is_team_game)
        ) and (
            old_status == RsvpStatus.REQUESTED_TO_JOIN and
            new_status == RsvpStatus.GOING
        ))
        return (user_is_player and is_rsvp) or is_request_accept


class RsvpsList(ListCreateAPIView):
    """List players RSVPs for a specific game"""
    serializer_class = RsvpDetailsSerializer
    permission_classes = RsvpCreateUpdateDestroyPermission,

    def get_queryset(self):
        return RsvpStatus.objects.filter(game_id=self.kwargs['game_id'])


class RsvpDetails(RetrieveUpdateDestroyAPIView):
    """Get or update player RSVP status"""
    serializer_class = RsvpSerializer
    permission_classes = RsvpCreateUpdateDestroyPermission,

    def get_queryset(self):
        return RsvpStatus.objects.filter(game_id=self.kwargs['game_id'])


class LocationsList(ListCreateAPIView):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
