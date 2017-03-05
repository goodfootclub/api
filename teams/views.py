import django_filters.rest_framework

from main.viewsets import AppViewSet

from .models import Team, Role
from .serializers import (
    RoleSerializer,
    RoleCreateSerializer,
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
    serializer_class = TeamDetailsSerializer
    serializer_classes = {
        'list': TeamListSerializer,
        'create': TeamCreateSerializer,
        'retrieve': TeamDetailsSerializer,
    }
    search_fields = ('info', 'name')

    def list(self, *args, **kwargs):
        """Get a list of existing teams or create a new one"""
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
    """
    Manage player "roles" using this api
    """
    serializer_class = RoleSerializer
    serializer_classes = {
        'create': RoleCreateSerializer,
    }

    def get_queryset(self):
        return Role.objects.filter(team_id=self.kwargs['team_pk'])
