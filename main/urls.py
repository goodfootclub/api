from django.conf.urls import url, include

from .views import ApiRoot


urlpatterns = [
    # Api root
    url(r'^$', ApiRoot.as_view(), name='api-root'),

    url(r'^users/', include('users.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^games/', include('games.urls')),
]
