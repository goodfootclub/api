"""api/users/ URLs"""

from django.conf.urls import url

from .views import CurrentUser, PlayersList


urlpatterns = [
    # Current user
    url(r'^me/$', CurrentUser.as_view(), name='current-user'),
    url(r'^players/$', PlayersList.as_view(), name='players-list'),
]
