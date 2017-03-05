from rest_framework.serializers import ModelSerializer

from ..models import User
from teams.views import TeamListSerializer
from games.views import GameListSerializer


__all__ = ['UserSerializer', 'CurrentUserSerializer']


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'bio', 'birthday', 'cover', 'first_name',
                  'gender', 'img', 'last_name')


class CurrentUserSerializer(UserSerializer):
    managed_teams = TeamListSerializer(many=True, read_only=True)
    games = GameListSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'phone', 'email', 'managed_teams', 'games'
        )
