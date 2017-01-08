from django.db import IntegrityError
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
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


class LocationSerializer(ModelSerializer):

    class Meta:
        model = Location


class RsvpSerializer(ModelSerializer):
    rsvp = ChoiceField(RsvpStatus.RSVP_CHOICES, source='status')
    rsvp_id = ReadOnlyField(source='id')
    id = IntegerField(source='player_id')

    class Meta:
        model = RsvpStatus
        fields = 'id', 'rsvp_id', 'rsvp', 'team'

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


class RsvpDetailsSerializer(RsvpSerializer):

    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')
    img = ImageField(source='player.img', read_only=True)

    class Meta(RsvpSerializer.Meta):
        fields = RsvpSerializer.Meta.fields + (
            'first_name', 'last_name', 'img'
        )


class GameListSerializer(ModelSerializer):

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


class GameSerializer(ModelSerializer):

    players = RsvpSerializer(source='rsvps', many=True)

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
    serializer_class = GameListSerializer
    queryset = Game.objects.all()


class GameDetails(RetrieveUpdateDestroyAPIView):
    """Check game details, change the info or delete it

    # Detailed view
    To get related models in a serialized form instad of ids
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


class RsvpsList(ListCreateAPIView):
    """List players RSVPs for a specific game"""
    serializer_class = RsvpDetailsSerializer

    def get_queryset(self):
        return RsvpStatus.objects.filter(game_id=self.kwargs['game_id'])


class RsvpDetails(RetrieveUpdateDestroyAPIView):
    """Get or update player RSVP status"""
    serializer_class = RsvpSerializer

    def get_queryset(self):
        return RsvpStatus.objects.filter(game_id=self.kwargs['game_id'])
