"""api/games URLs"""
from django.conf.urls import url
from rest_framework_nested import routers

from .views import GameViewSet, LocationViewSet, RsvpViewSet


router = routers.SimpleRouter()
router.register(r'games', GameViewSet)
router.register(r'locations', LocationViewSet)

games_router = routers.NestedSimpleRouter(router, r'games', lookup='game')
games_router.register(r'players', RsvpViewSet, base_name='rsvp')

urlpatterns = router.urls + games_router.urls
