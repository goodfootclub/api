"""Users app views

CurrentUser (api/users/current) - shows info about logged in user or 401s.
"""
from django.contrib.postgres.search import SearchVector
from rest_framework.pagination import LimitOffsetPagination
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

    def get_queryset(self):
        """Apply a simple text search to the Player query
        """
        queryset = User.objects.all()
        search = self.request.query_params.get('search', None)
        if search is not None:
            queryset = queryset.annotate(
                search=SearchVector('first_name', 'last_name', 'bio'),
            ).filter(search=search)
        return queryset


class PlayerDetails(RetrieveAPIView):
    serializer_class = PlayerDetailsSerializer
    queryset = User.objects.all()
