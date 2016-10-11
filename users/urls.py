"""api/users/ urls """

from django.conf.urls import url

from .views import CurrentUser


urlpatterns = [
    # Current user
    url(r'^current/?$', CurrentUser.as_view(), name='current-user'),
]
