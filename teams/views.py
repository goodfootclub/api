from django.contrib.postgres.search import SearchVector

from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response

from main.viewsets import AppViewSet

from .models import Team, Role
from .serializers import (
    RoleSerializer,
    TeamCreateSerializer,
    TeamDetailsSerializer,
    TeamListSerializer,
)
# from games.views import GamesList


class TeamViewSet(AppViewSet):
    """
    Root viewset for teams api
    """
    queryset = Team.objects.all()
    # serializer_class = TeamDetailsSerializer
    serializer_class = TeamDetailsSerializer
    serializer_classes = {
        'list': TeamListSerializer,
        'create': TeamCreateSerializer,
        'retrieve': TeamDetailsSerializer,
    }

    def list(self, *args, **kwargs):
        """Get a list of existing teams or make a new one"""
        return super().list(*args, **kwargs)

    def retrieve(self, *args, **kwargs):
        """
        Check details of a team, change the info or delete it

        # Players
        Team players can be managed throught a separate method at
        the [teams/{id}/players/](./players) view.
        """
        return super().retrieve(*args, **kwargs)


class RoleViewSet(AppViewSet):
    """ Testing VeiwSets """
    serializer_class = RoleSerializer

    def get_queryset(self):
        return Role.objects.filter(team_id=self.kwargs['team_pk'])
