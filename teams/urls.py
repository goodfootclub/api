"""api/teams URLs"""
from django.conf.urls import url

from .views import TeamsList, TeamDetails


urlpatterns = [
    url(r'^_?/?$', TeamsList.as_view(), name='teams-list'),
    url(r'^_?/(?P<pk>\d+)/?$', TeamDetails.as_view(),
        name='team-detail'),
]
