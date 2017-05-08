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

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'phone', 'email', 'managed_teams',
        )

    def to_representation(self, user: User):
        data = super().to_representation(user)

        inv_total, inv_games, inv_teams = user.get_invites_counts()
        if inv_total:
            data['invites'] = {'total': inv_total}
            if inv_games:
                data['invites']['games'] = inv_games
            if inv_teams:
                data['invites']['teams'] = inv_teams

        return data
