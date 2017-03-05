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
    'TeamCreateSerializer',
    'TeamDetailsSerializer',
    'TeamListSerializer',
]


class TeamListSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = 'id', 'name', 'info', 'type'

    def to_representation(self, obj):
        data = super().to_representation(obj)

        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse('team-detail', (obj.id, ),
                                  request=request)
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
