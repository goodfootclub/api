from django.db.models import Count
from rest_framework import permissions
from rest_framework.decorators import list_route
from rest_framework_gis.filters import InBBoxFilter

from main.viewsets import AppViewSet
from .models import Game, Location, RsvpStatus
from .permissions import GameUpdateDestroyPermission
from .serializers import (
    GameCreateSerializer,
    GameDetailsSerializer,
    GameListSerializer,
    LocationSerializer,
    RsvpCreateSerializer,
    RsvpSerializer,
)


class GameViewSet(AppViewSet):
    """
    # Games Api

    Root viewset for api/games, also included in api/teams/{id}/games/

    list:

    Get a list of upcoming pickup games\n
    Can be searched by name, date, location name, location address.\n
    Can be ordered by `datetime` (default) and `-datetime`.

    create:

    Create a game\n
    You can create many copies at different dates at once
    by specifying multiple dates in `datetimes` property

    retrieve:

    Get a specific game\n
    Players are managed through a separate endpoint: `games/{id}/players`

    update: Update the game

    partial_update: Update the game (partial)

    destroy: Delete the game (hard)
    """
    queryset = Game.objects.all()\
        .select_related('location')\
        .prefetch_related('teams')

    serializer_class = GameDetailsSerializer
    serializer_classes = {
        'list': GameListSerializer,
        'create': GameCreateSerializer,
        'invites': GameListSerializer,
        'my': GameListSerializer,
    }

    permission_classes = (
        permissions.IsAuthenticated,
        GameUpdateDestroyPermission
    )

    ordering_fields = ('datetime', )
    search_fields = ('datetime', 'location__name', 'location__address', 'name')
    bbox_filter_field = 'location__gis'
    filter_backends = (InBBoxFilter, )

    def get_queryset(self):
        """
        Depending on action and query params either:
         - my games (with my rsvp status)
         - team games for `/teams/{team_pk}/games/` api
         - pickup games for `/games/` api
        """
        queryset = super().get_queryset()

        if self.action not in ['invites', 'list', 'my']:  # not list
            return queryset

        queryset = queryset.with_rsvps(self.request.user)

        if self.action == 'my':
            queryset = queryset.filter(rsvp__gt=RsvpStatus.INVITED)

        if self.action == 'invites':
            return queryset.filter(rsvp=RsvpStatus.INVITED)

        if 'team_pk' in self.kwargs:
            # Team games for a specific team
            queryset = queryset.filter(teams__in=[self.kwargs['team_pk']])
        elif self.action == 'list':
            # Pickup games
            queryset = queryset.filter(teams=None)

        if 'all' in self.request.query_params:
            return queryset

        return queryset.future()

    def get_markers(self, queryset):
        """
        Get locations data with count of games
        """
        data = queryset.values(
            'location__id',
            'location__name',
            'location__address',
            'location__gis',
        )
        # import pdb
        # pdb.set_trace()
        data = queryset.values(
            'location__id',
            'location__name',
            'location__address',
        ).annotate(games=Count('location__id'))
        return data

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        res = self.get_paginated_response(serializer.data)
        res.data['map'] = {'markers': 'TODO'}  # self.get_markers(queryset)}
        res.data.move_to_end('results')
        return res

    @list_route(methods=['get'])
    def my(self, *args, **kwargs):
        """Games for the logged in user"""
        return self.list(*args, **kwargs)

    @list_route(methods=['get'])
    def invites(self, *args, **kwargs):
        """Pending game invites for the logged-in user"""
        return self.list(*args, **kwargs)


class LocationViewSet(AppViewSet):
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    search_fields = ('address', 'name')
    bbox_filter_field = 'gis'
    filter_backends = (InBBoxFilter, )


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

        data = request.data

        if not data:
            return True

        try:
            new_status = int(data.get('rsvp', None))
            new_player_id = int(data.get('id', None))
        except (TypeError, ValueError):
            # It will raise a validation error during serializing
            # and produce a sensible error message so here we can give
            # id it green light without worries
            return True

        new_team = data.get('team', None)
        # Only pickup games for now, No teams allowed yet
        if new_team and new_team != RsvpStatus.NO_TEAM:
            # TODO: Check permission to be on that team
            pass

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
        try:
            new_status = int(data.get('rsvp', None))
        except ValueError:
            return True  # Will be stopped by serializer validator

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
    permission_classes = (
        permissions.IsAuthenticated,
        RsvpCreateUpdateDestroyPermission,
    )

    def get_queryset(self):
        return super().get_queryset().filter(game_id=self.kwargs['game_pk'])
