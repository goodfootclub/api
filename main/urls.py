from django.conf.urls import url, include

from .views import (
    ApiRoot,
    TeamsList,
    TeamDetails,
    GamesList,
    GameDetails,
    LocationsList,
    LocationDetails,
)


urlpatterns = [
    # Api root
    url(r'^$', ApiRoot.as_view(), name='api-root'),

    # Old Teams api
    url(r'^old-teams/?$', TeamsList.as_view(), name='old-teams-list'),
    url(r'^old-teams/(?P<pk>\d+)/?$', TeamDetails.as_view(),
        name='old-team-detail'),

    # Games api
    url(r'^games/?$', GamesList.as_view(), name='games-list'),
    url(r'^games/(?P<pk>\d+)/?$', GameDetails.as_view(),
        name='game-detail'),

    # Locations api
    url(r'^locations/?$', LocationsList.as_view(),
        name='locations-list'),
    url(r'^locations/(?P<pk>\d+)/?$', LocationDetails.as_view(),
        name='location-detail'),

    # Users api
    url(r'^users/', include('users.urls')),

    # Teams api
    url(r'^teams/', include('teams.urls')),
]
