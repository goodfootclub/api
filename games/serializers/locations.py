from rest_framework.serializers import ModelSerializer
from ..models import Location


__all__ = ['LocationSerializer']


class LocationSerializer(ModelSerializer):

    class Meta:
        model = Location
