from django.db import IntegrityError
from django.db.transaction import atomic

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.reverse import reverse
from rest_framework.serializers import (
    ModelSerializer,
    ReadOnlyField,
    ImageField,
)

from main.exceptions import RelationAlreadyExist
from users.views import PlayerListSerializer
from .models import Team, Role


class RoleSerializer(ModelSerializer):

    role_id = ReadOnlyField(source='id')
    id = ReadOnlyField(source='player_id')

    class Meta:
        model = Role
        fields = 'id', 'role', 'role_id'

    def to_representation(self, obj):
        data = super().to_representation(obj)
        request = self.context.get('request', None)

        if request and request.accepted_renderer.format == 'api':
            try:
                data['url'] = reverse(
                    'team-role',
                    (self.context['view'].kwargs['team_id'], obj.id),
                    request=request
                )
            except KeyError:
                pass
        return data

    def create(self, validated_data):
        if 'team_id' not in validated_data:
            validated_data.update(self.context['view'].kwargs)
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise RelationAlreadyExist(
                detail=e.args[0].split('DETAIL:  ')[1]
            )


class RoleDetailsSerializer(RoleSerializer):

    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')
    img = ImageField(source='player.img')

    class Meta(RoleSerializer.Meta):
        fields = RoleSerializer.Meta.fields + (
            'first_name', 'last_name', 'img'
        )


class TeamListSerializer(ModelSerializer):

    class Meta:
        model = Team
        fields = 'id', 'name', 'type'

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
                record = {'player': record}
            r, created = roles_query.get_or_create(
                player_id=record['player'], team_id=data['id']
            )
            if not created:
                roles_by_id.pop(r.id)
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


class TeamsList(ListCreateAPIView):
    """Get a list of existing teams or make a new one"""
    serializer_class = TeamListSerializer
    queryset = Team.objects.all()


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
    """List of players on the team"""
    serializer_class = RoleDetailsSerializer

    def get_queryset(self):
        return Role.objects.filter(team_id=self.kwargs['team_id'])


class RoleDetails(RetrieveUpdateDestroyAPIView):
    """Get or update specific player role"""
    serializer_class = RoleDetailsSerializer

    def get_queryset(self):
        return Role.objects.filter(team_id=self.kwargs['team_id'])
