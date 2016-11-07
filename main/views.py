"""Main app views

ApiRoot (api/) - shows available api endpoints and a readme in the
    browsable view.
"""

from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.serializers import ModelSerializer

from .models import Team, Game, Location


class ApiRoot(APIView):
    """
    # Welcome to The Good Foot Club API

    TODO: some readme should go there

    ## Explore

    Down below you can see the list of available api methods. Feel free to
    follow each url and learn details about each method.
    """

    def get(self, request, format=None):
        return Response({
            'api-root': reverse('api-root', request=request, format=format),
            'current-user':
                reverse('current-user', request=request, format=format),
            'games-list':
                reverse('games-list', request=request, format=format),
            'locations-list':
                reverse('locations-list', request=request, format=format),
            'teams-list':
                reverse('teams-list', request=request, format=format),
        })


##
# Teams API
##

class TeamSerializer(ModelSerializer):
    class Meta:
        model = Team


class TeamsList(ListCreateAPIView):
    """
    # Teams

    Get a list of teams or make a new one!
    """
    serializer_class = TeamSerializer
    queryset = Team.objects.all()


class TeamDetails(RetrieveUpdateDestroyAPIView):
    """
    # Teams

    Check details of a team, change the info or delete it!
    """
    serializer_class = TeamSerializer
    queryset = Team.objects.all()


##
# Games API
##

class GameSerializer(ModelSerializer):
    class Meta:
        model = Game


class GamesList(ListCreateAPIView):
    """
    # Games

    Get a list of Games or make a new one!
    """
    serializer_class = GameSerializer
    queryset = Game.objects.all()


class GameDetails(RetrieveUpdateDestroyAPIView):
    """
    # Game

    Check details of a Game, change the info or delete it!
    """
    serializer_class = GameSerializer
    queryset = Game.objects.all()


##
# Locations API
##

class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location


class LocationsList(ListCreateAPIView):
    """
    # Locations

    Get a list of Locations or make a new one!
    """
    serializer_class = LocationSerializer
    queryset = Location.objects.all()


class LocationDetails(RetrieveUpdateDestroyAPIView):
    """
    # Location

    Check details of a Location, change the info or delete it!
    """
    serializer_class = LocationSerializer
    queryset = Location.objects.all()

