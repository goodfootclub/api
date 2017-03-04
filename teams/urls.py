"""api/teams URLs"""
from django.conf.urls import url, include
from rest_framework_nested import routers

from .views import TeamsViewSet, RolesViewSet


router = routers.SimpleRouter()
router.register(r'teams', TeamsViewSet)

teams_router = routers.NestedSimpleRouter(router, r'teams', lookup='team')
teams_router.register(r'players', RolesViewSet, base_name='team-role')
# TODO: teams_router.register(r'games', GamesViewSet)

urlpatterns = router.urls + teams_router.urls
