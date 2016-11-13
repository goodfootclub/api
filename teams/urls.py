"""api/teams URLs"""
from django.conf.urls import url

from .views import TeamsList, TeamDetails, RolesList, RoleDetails


urlpatterns = [url(
    r'^$',
    TeamsList.as_view(),
    name='teams-list'
), url(
    r'^(?P<team_id>\d+)/$',
    TeamDetails.as_view(),
    name='team-detail'
), url(
    r'^(?P<team_id>\d+)/players/$',
    RolesList.as_view(),
    name='team-roles'
), url(
    r'^(?P<team_id>\d+)/players/(?P<pk>\d+)/$',
    RoleDetails.as_view(),
    name='team-role'
)]
