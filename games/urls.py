"""api/games URLs"""
from django.conf.urls import url
from rest_framework_nested import routers

from .views import GameViewSet, LocationViewSet


router = routers.SimpleRouter()
router.register(r'games', GameViewSet)
router.register(r'locations', LocationViewSet)

urlpatterns = router.urls
