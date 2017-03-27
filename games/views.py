from datetime import datetime

from rest_framework import permissions
from rest_framework.decorators import list_route

from main.viewsets import AppViewSet
from .models import Game, Location, RsvpStatus
from .serializers import (
    GameCreateSerializer,
    GameDetailsSerializer,
    GameListSerializer,
    GameSerializer,
    LocationSerializer,
    RsvpCreateSerializer,
    RsvpSerializer,
)


class GameViewSet(AppViewSet):
    """
    Root viewset for games api, also included in teams/{id}/games api
    """
    queryset = Game.objects.all()
    serializer_class = GameDetailsSerializer
    serializer_classes = {
        'list': GameListSerializer,
        'create': GameCreateSerializer,
    }
    ordering_fields = ('datetime', )
    search_fields = ('datetime', 'location__name', 'location__address')

    def get_queryset(self):
        """
        Only return games in the future unless 'all' param is specified,
        filter by team if required or list games for logged in user.
        """
        queryset = super().get_queryset()

        if 'team_pk' in self.kwargs:
            queryset = queryset.filter(teams__in=[self.kwargs['team_pk']])

        if self.action == 'my':
            queryset = queryset.filter(players__in=[self.request.user])

        if 'team_pk' not in self.kwargs and self.action == 'list':
            # show pickup games only
            queryset = queryset.filter(teams=None)

        if (
            self.action not in ('list', 'my') or
            'all' in self.request.query_params
        ):
            return queryset

        return queryset.filter(datetime__gt=datetime.utcnow())

    @list_route(methods=['get'])
    def my(self, request):
        """Games for the logged in user"""
        return super().list(request)


class LocationViewSet(AppViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    search_fields = ('address', 'name')


# TODO: move to a separate permissions module
class RsvpCreateUpdateDestroyPermission(permissions.BasePermission):
    """
    Ensure that the change is withing the following options:
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

            game = Game.objects.get(id=view.kwargs['game_pk'])
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
        user_is_team_manager = False
        try:
            team = game.teams.all()[obj.team]
            user_is_team_manager = user in team.managers.all()
        except IndexError:
            team = None
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

        new_status = int(data.get('rsvp', None))
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


class RsvpViewSet(AppViewSet):
    serializer_class = RsvpSerializer
    serializer_classes = {
        'create': RsvpCreateSerializer,
    }
    queryset = RsvpStatus.objects.all()
    permission_classes = RsvpCreateUpdateDestroyPermission,

    def get_queryset(self):
        return super().get_queryset().filter(game_id=self.kwargs['game_pk'])
