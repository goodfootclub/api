"""api/users/ URLs"""

from django.conf.urls import url

from .views import CurrentUser, PlayerList, PlayerDetails


urlpatterns = [
    # Current user
    url(r'^me/$', CurrentUser.as_view(), name='current-user'),
    url(r'^players/$', PlayerList.as_view(), name='player-list'),
    url(r'^players/(?P<pk>\d+)/$', PlayerDetails.as_view(),
        name='player-details'),
]
