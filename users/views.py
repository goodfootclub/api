"""Users app views

CurrentUser (api/users/current) - shows info about logged in user or 401s.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.generics import RetrieveUpdateAPIView

from .models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'bio', 'birthday', 'cover', 'email', 'first_name',
                  'gender', 'img', 'last_name', 'phone',)


class CurrentUser(RetrieveUpdateAPIView):
    """Information about currently logged in user."""
    permission_classes = (IsAuthenticated, )
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
