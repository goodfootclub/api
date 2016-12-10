"""api/users/ URLs"""

from django.conf.urls import url

from .views import CurrentUser


urlpatterns = [
    # Current user
    url(r'^me/$', CurrentUser.as_view(), name='current-user'),
]
