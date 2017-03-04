from django.conf.urls import url, include

from .views import ApiRoot, ApiError


urlpatterns = [
    # Api root
    url(r'^$', ApiRoot.as_view(), name='api-root'),
    url(r'^error/$', ApiError.as_view(), name='api-error'),

    url(r'^users/', include('users.urls')),
    url(r'^', include('teams.urls')),
    url(r'^games/', include('games.urls')),
]
