from django.shortcuts import get_object_or_404

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
from .models import Team, Role


class RoleSerializer(ModelSerializer):

    player_id = ReadOnlyField(source='player.id')
    first_name = ReadOnlyField(source='player.first_name')
    last_name = ReadOnlyField(source='player.last_name')

    class Meta:
        model = Role
        fields = 'id', 'player_id', 'role', 'first_name', 'last_name'


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


class TeamsList(ListCreateAPIView):
    """
    # Teams

    Get a list of teams or make a new one
    """
    serializer_class = TeamListSerializer
    queryset = Team.objects.all()


class TeamDetailsSerializer(ModelSerializer):

    players = RoleSerializer(source='role_set', many=True)

    class Meta:
        model = Team

    def to_internal_value(self, data):
        d = dict(data)

        if 'players' not in data:
            return data

        roles = []
        for player in data['players']:
            r = Role.objects.get_or_create(
                player_id=player, team_id=data['id']
            )
            if '':
                pass

        raise Exception('test')


class TeamDetails(RetrieveUpdateDestroyAPIView):
    """
    # Teams

    Check details of a team, change the info or delete it
    """
    serializer_class = TeamDetailsSerializer
    queryset = Team.objects.all()

    # def get_object(self):
    #     queryset = self.get_queryset()
    #     obj = get_object_or_404(queryset, id=self.kwargs['pk'])

    #     obj.players_ = [{
    #         'id': role.id,
    #         'player_id': role.player_id,
    #         'first_name': role.player.first_name,
    #         'last_name': role.player.last_name,
    #         'role': role.role,
    #     } for role in Role.objects.filter(team=obj)]

    #     return obj
