"""Main app views

ApiRoot (api/) - shows available api endpoints and a readme in the
    browsable view.
"""
from collections import OrderedDict

from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.views import APIView

from users.views import UserSerializer
from .models import Team, Game, Location


# API endpoints names (as in 'urls.py' files) to display on ApiRoot
API_METHODS = [
    'api-root',
    'current-user',
    'games-list',
    'locations-list',
    'old-teams-list',
    'teams-list',
]


class ApiRoot(APIView):
    """
    # Welcome to The Good Foot Club API

    Welcome to The Good Foot Club project REST API!

    ## Explore

    Down below you can see the list of available api methods. Feel free to
    follow each url and learn details about each method.
    """

    def get(self, request, format=None):

        data = OrderedDict()

        for method in API_METHODS:
            data[method] = reverse(method, request=request, format=format)

        return Response(data)


##
# Teams API
##

class TeamSerializer(ModelSerializer):

    class Meta:
        model = Team

    def __init__(self, *args, **kwargs):
        """If parameter 'd' or 'details' is in the query, show related
        objects in a detailed representation so the front end doesn't
        need to hit multiple API endpoints. Otherwise, just return ids
        """
        super().__init__(*args, **kwargs)

        request = self.context.get('request', None)
        if request and {'d', 'details'} & request.query_params.keys():
            self.fields['players'] = UserSerializer(many=True)
            self.fields['manager'] = UserSerializer()


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


##
# Games API
##

class GameSerializer(ModelSerializer):

    class Meta:
        model = Game

    def __init__(self, *args, **kwargs):
        """If parameter 'd' or 'details' is in the query, show related
        objects in a detailed representation so the front end doesn't
        need to hit multiple API endpoints. Otherwise, just return ids
        """
        super().__init__(*args, **kwargs)

        request = self.context['request']
        if request and {'d', 'details'} & request.query_params.keys():
            self.fields['location'] = LocationSerializer()
            self.fields['teams'] = TeamSerializer(many=True,
                                                  context=self.context)


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
