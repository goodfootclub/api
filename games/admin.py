from django.contrib import admin

from .models import Game, Location, RsvpStatus


admin.site.register(Game)
admin.site.register(Location)
admin.site.register(RsvpStatus)
