from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin

from .models import Game, Location, RsvpStatus


class LocationAdmin(GeoModelAdmin):
    openlayers_url = 'https://openlayers.org/api/2.13.1/OpenLayers.js'

admin.site.register(Game)
admin.site.register(Location, LocationAdmin)
admin.site.register(RsvpStatus)
