from django.db.transaction import atomic

from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ImageField,
    IntegerField,
    ModelSerializer,
    ReadOnlyField,
)

from users.serializers import PlayerListSerializer
from . import RoleSerializer, RoleDetailsSerializer
from ..models import Team


__all__ = [
    'TeamDetailsSerializer',
    'TeamListSerializer',
    'TeamSerializer',
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

    def create(self, *args, **kwargs):
        team = super().create(*args, **kwargs)
        request = self.context.get('request', None)
        if request:
            team.managers.add(request.user)
        return team


class TeamSerializer(ModelSerializer):

    players = RoleSerializer(source='role_set', many=True)

    class Meta:
        model = Team

    def to_internal_value(self, data):
        if 'players' not in data:
            return data

        roles_query = Role.objects.filter(team_id=data['id'])
        roles_by_id = {
            role.id: role
            for role in roles_query
        }
        roles = []
        for record in data['players']:
            if isinstance(record, int):
                record = roles_by_id.get(record, {'id': record})
            r, created = roles_query.get_or_create(
                player_id=record['id'], team_id=data['id']
            )
            if not created:
                roles_by_id.pop(r.id, None)
            r.role = record.get('role', r.role)
            roles.append(r)
        data['players'] = roles
        data['players_to_remove'] = roles_by_id.values()

        return data

    @atomic
    def update(self, instance, validated_data):
        for role in validated_data.pop('players', []):
            role.save()

        for role in validated_data.pop('players_to_remove', []):
            role.delete()

        return super().update(instance, validated_data)


class TeamDetailsSerializer(TeamSerializer):
    players = RoleDetailsSerializer(source='role_set', many=True)
    managers = PlayerListSerializer(many=True)

    def to_internal_value(self, data):

        data = super().to_internal_value(data)

        data['managers'] = [
            user if isinstance(user, int) else user['id']
            for user in data.get('managers', [])
        ]

        return data

    def update(self, instance, validated_data):

        instance.managers = validated_data.pop('managers', [])

        return super().update(instance, validated_data)
