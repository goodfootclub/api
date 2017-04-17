from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Game, Location, RsvpStatus


class LocationAdmin(OSMGeoAdmin):
    openlayers_url = 'https://openlayers.org/api/2.13.1/OpenLayers.js'

admin.site.register(Game)
admin.site.register(Location, LocationAdmin)
admin.site.register(RsvpStatus)
