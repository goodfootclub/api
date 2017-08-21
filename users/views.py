"""Users app views

CurrentUser (api/users/current) - shows info about logged in user or 401s.
"""
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from .models import User
from .serializers import (
    CurrentUserSerializer,
    PlayerListSerializer,
    PlayerDetailsSerializer
)


class CurrentUser(RetrieveUpdateDestroyAPIView):
    """
    Information about currently logged in user.
    """
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance: User):
        instance.is_active = False
        instance.save()


class PlayerList(ListAPIView):
    serializer_class = PlayerListSerializer
    queryset = User.objects.all()
    search_fields = ('first_name', 'last_name', 'bio')


class PlayerDetails(RetrieveAPIView):
    serializer_class = PlayerDetailsSerializer
    queryset = User.objects.all()
