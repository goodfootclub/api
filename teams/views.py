from django.contrib.postgres.search import SearchVector

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)


from .models import Team, Role
from .serializers import (
    RoleDetailsSerializer,
    RoleSerializer,
    TeamDetailsSerializer,
    TeamListSerializer,
    TeamSerializer,
)
# from games.views import GamesList


class TeamsList(ListCreateAPIView):
    """Get a list of existing teams or make a new one"""
    serializer_class = TeamListSerializer

    def get_queryset(self):
        """Apply a simple text search to the Player query
        """
        queryset = Team.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.annotate(
                search=SearchVector('name', 'info'),
            ).filter(search=search)
        return queryset


class TeamDetails(RetrieveUpdateDestroyAPIView):
    """Check details of a team, change the info or delete it

    # Detailed view
    To get related models in a serialized form instad of ids
    [detailed view](?details) is available

    # Players
    You can update players in this method or manage them separatly on
    the [teams/{id}/players/](./players) view
    """
    queryset = Team.objects.all()
    lookup_url_kwarg = 'team_id'

    def get_serializer_class(self):
        if {'d', 'details'} & self.request.query_params.keys():
            return TeamDetailsSerializer
        return TeamSerializer


class RolesList(ListCreateAPIView):
    """List of players on the team

    Add a player by POSTing to this endpoint
    """
    serializer_class = RoleDetailsSerializer

    def get_queryset(self):
        return Role.objects.filter(team_id=self.kwargs['team_id'])


class RoleDetails(RetrieveUpdateDestroyAPIView):
    """Get or update specific player role"""
    serializer_class = RoleDetailsSerializer

    def get_queryset(self):
        return Role.objects.filter(team_id=self.kwargs['team_id'])
