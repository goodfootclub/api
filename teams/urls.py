"""api/teams URLs"""
from django.conf.urls import url, include
from rest_framework_nested import routers

from games.views import GameViewSet
from .views import TeamViewSet, RoleViewSet


router = routers.SimpleRouter()
router.register(r'teams', TeamViewSet)

teams_router = routers.NestedSimpleRouter(router, r'teams', lookup='team')
teams_router.register(r'players', RoleViewSet, base_name='team-role')
teams_router.register(r'games', GameViewSet, base_name='team-games')

urlpatterns = router.urls + teams_router.urls
