import django_filters.rest_framework
from rest_framework.decorators import list_route

from main.viewsets import AppViewSet
from .models import Team, Role
from .serializers import (
    MyTeamListSerializer,
    RoleCreateSerializer,
    RoleSerializer,
    TeamCreateSerializer,
    TeamDetailsSerializer,
    TeamListSerializer,
)


class TeamViewSet(AppViewSet):
    """
    Root viewset for teams api
    """
    queryset = Team.objects.all()
    serializer_class = TeamDetailsSerializer
    serializer_classes = {
        'list': TeamListSerializer,
        'my': MyTeamListSerializer,
        'create': TeamCreateSerializer,
        'retrieve': TeamDetailsSerializer,
    }
    search_fields = ('info', 'name')

    def get_queryset(self):
        if self.action == 'my':
            return Role.objects.all().filter(player=self.request.user)
        else:
            return super().get_queryset()

    def list(self, *args, **kwargs):
        """Get a list of existing teams or create a new one

        # My Teams
        Teams for the logged-in user are available at
        [/api/teams/my/](/api/teams/my/)
        """
        return super().list(*args, **kwargs)

    @list_route(methods=['get'])
    def my(self, request):
        """Teams for the logged in user"""
        return super().list(request)

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
