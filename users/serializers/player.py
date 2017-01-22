from rest_framework.serializers import ModelSerializer

from ..models import User


__all__ = ['PlayerListSerializer', 'PlayerDetailsSerializer']


class PlayerListSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = 'id', 'bio', 'first_name', 'img', 'last_name'


class PlayerDetailsSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = 'id', 'bio', 'cover', 'first_name', 'img', 'last_name'
