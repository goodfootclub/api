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

    # Teams api
    url(r'^teams/?$', TeamsList.as_view(), name='teams-list'),
    url(r'^teams/(?P<pk>\d+)/?$', TeamDetails.as_view(),
        name='team-detail'),

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
]
