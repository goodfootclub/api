from django.shortcuts import get_object_or_404
from django.db.transaction import atomic

from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    Field,
    ReadOnlyField,
    HyperlinkedModelSerializer,
    ModelSerializer,
    Serializer,
)

from users.views import UserSerializer
from users.models import User
from .models import Team, Role


class RoleSerializer(ModelSerializer):

    class Meta:
        model = Role
        fields = 'id', 'player', 'role'


class RoleDetailsSerializer(ModelSerializer):

    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')

    class Meta:
        model = Role
        fields = 'id', 'player', 'role', 'first_name', 'last_name'


class TeamListSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = 'id', 'name'

    def to_representation(self, obj):
        data = super().to_representation(obj)

        request = self.context.get('request', None)
        if request and request.accepted_renderer.format == 'api':
            data['url'] = reverse('team-detail', (obj.id, ),
                                  request=request)
        return data


class TeamSerializer(ModelSerializer):

    players = RoleSerializer(source='role_set', many=True)

    class Meta:
        model = Team


class TeamDetailsSerializer(ModelSerializer):

    players = RoleDetailsSerializer(source='role_set', many=True)
    managers = UserSerializer(many=True)

    class Meta:
        model = Team

    def to_internal_value(self, data):

        roles = []
        for record in data.get('players', []):
            if isinstance(record, int):
                record = {'player_id': record}
            r, _ = Role.objects.get_or_create(
                player_id=record['player_id'], team_id=data['id']
            )
            r.role = record.get('role', r.role)
            roles.append(r)
        data['players'] = roles

        data['managers'] = [
            1 if isinstance(user, int) else user['id']
            for user in data.get('managers', [])
        ]

        return data

    @atomic
    def update(self, instance, validated_data):
        for role in validated_data.pop('players', []):
            role.save()

        instance.managers = validated_data.pop('managers', [])

        return super().update(instance, validated_data)


class TeamsList(ListCreateAPIView):
    """Get a list of existing teams or make a new one"""
    serializer_class = TeamListSerializer
    queryset = Team.objects.all()


class TeamDetails(RetrieveUpdateDestroyAPIView):
    """Check details of a team, change the info or delete it

    # Detailed view
    To get related models in a serialized form instad of ids
    [detailed view](?details) is available
    """
    queryset = Team.objects.all()

    def get_serializer_class(self):
        if {'d', 'details'} & self.request.query_params.keys():
            return TeamDetailsSerializer
        return TeamSerializer
