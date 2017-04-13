from django.db.transaction import atomic

from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ImageField,
    IntegerField,
    ModelSerializer,
    ReadOnlyField,
)

from users.serializers import PlayerListSerializer
from . import RoleSerializer
from ..models import Team


__all__ = [
    'MyTeamListSerializer',
    'TeamCreateSerializer',
    'TeamDetailsSerializer',
    'TeamListSerializer',
]


class TeamListSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = 'id', 'name', 'info', 'type'

    def to_representation(self, team):
        data = super().to_representation(team)

        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse('team-detail', (team.id, ),
                                  request=request)
        return data


class MyTeamListSerializer(TeamListSerializer):
    """
    This takes a *Role* object instead of a Team object, but only uses
    status from it, rest of the fields are for respective .team
    """

    def to_representation(self, role):
        data = super().to_representation(role.team)
        data['role'] = role.role
        return data


class TeamCreateSerializer(TeamListSerializer):

    def create(self, *args, **kwargs):
        team = super().create(*args, **kwargs)
        request = self.context.get('request', None)
        if request:
            team.managers.add(request.user)
        return team


class TeamDetailsSerializer(ModelSerializer):

    players = RoleSerializer(source='role_set', many=True, read_only=True)
    managers = PlayerListSerializer(many=True, read_only=True)
    name = ReadOnlyField()

    class Meta:
        model = Team
        fields = 'id', 'name', 'info', 'type', 'players', 'managers'
