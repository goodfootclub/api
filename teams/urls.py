"""api/teams URLs"""
from django.conf.urls import url

from .views import TeamsList, TeamDetails


urlpatterns = [
    url(r'^/?$', TeamsList.as_view(), name='teams-list'),
    url(r'^/(?P<pk>\d+)/?$', TeamDetails.as_view(),
        name='team-detail'),
]
