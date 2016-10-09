"""Main app views

ApiRoot (api/) - shows available api endpoints and a readme in the
    browsable view.
"""

from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


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
            'api-root': reverse('api-root', request=request, format=format)
        })
