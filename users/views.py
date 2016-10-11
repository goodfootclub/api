"""Users app views

CurrentUser (api/users/current) - shows info about logged in user or 401s.
"""
from django.contrib.auth.models import User

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class CurrentUser(APIView):
    """Information about currently logged in user."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        return Response(
            UserSerializer(request.user).data
        )
