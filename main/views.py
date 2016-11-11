"""Main app views

ApiRoot (api/) - shows available api endpoints and a readme in the
    browsable view.
"""
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.serializers import ModelSerializer, Serializer

from users.views import UserSerializer
from .models import Team, Game, Location


# FIXME: This doesn't work. I'll give it a second look in the morning
class OptionalFieldsMixin(ModelSerializer):
    """Optional fields on a serializer

    Include or swap some specified fields based on having a certain
    parameter(s) is in the query. For example initial api request
    may need detailed info to display it quickly and avoid hitting api
    multiple times, but after that, working with just ids is more efficient

    ```
    class MySerializer(ModelSerializer, OptionalFieldsMixin):

        class Meta:
            model = MyModel
            asdfoptional_fields_query_params = ('d', 'details')  # Default
            asdfoptional_fields = {
                'users': UserSerializer(many=True)
                # 'users' field will become an array of serialized
                # objects instead of an array of ids if one of the
                # parameters is in the query_params
            }
    ```
    """
    def __init__(self, *args, **kwargs):
        super(OptionalFieldsMixin, self).__init__(*args, **kwargs)

        if not hasattr(self.Meta, 'asdfoptional_fields'):
            return

        trigger_params = set(getattr(
            self.Meta,
            'asdfoptional_fields_query_params',
            ('d', 'details')
        ))

        request = self.context['request']
        if request and not trigger_params & request.query_params.keys():
            return

        for k in self.Meta.asdfoptional_fields:
            self.fields.pop(k)


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
