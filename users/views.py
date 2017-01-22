"""Users app views

CurrentUser (api/users/current) - shows info about logged in user or 401s.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    ListAPIView,
    RetrieveAPIView,
)

from .models import User
from .serializers import (
    CurrentUserSerializer,
    PlayerListSerializer,
    PlayerDetailsSerializer
)


class CurrentUser(RetrieveUpdateAPIView):
    """Information about currently logged in user.
    """
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user


class PlayerList(ListAPIView):
    serializer_class = PlayerListSerializer
    queryset = User.objects.all()


class PlayerDetails(RetrieveAPIView):
    serializer_class = PlayerDetailsSerializer
    queryset = User.objects.all()
