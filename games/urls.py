"""api/games URLs"""
from django.conf.urls import url

from .views import GamesList, GameDetails, RsvpsList, RsvpDetails


urlpatterns = [url(
    r'^$',
    GamesList.as_view(),
    name='games-list'
), url(
    r'^(?P<game_id>\d+)/$',
    GameDetails.as_view(),
    name='game-detail'
), url(
    r'^(?P<game_id>\d+)/players/$',
    RsvpsList.as_view(),
    name='game-rsvps'
), url(
    r'^(?P<game_id>\d+)/players/(?P<pk>\d+)/$',
    RsvpDetails.as_view(),
    name='game-rsvp'
)]
