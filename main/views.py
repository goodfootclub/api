"""Main app views

ApiRoot (api/) - shows available api endpoints and a readme in the
    browsable view.
"""
from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


# API endpoints names (as in 'urls.py' files) to display on ApiRoot
API_METHODS = [
    'api-root',
    'current-user',
    'games-list',
    # 'locations-list',
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
        """List of available API endpints"""
        data = OrderedDict()

        for method in API_METHODS:
            data[method] = reverse(method, request=request, format=format)

        return Response(data)
