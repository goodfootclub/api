from django.conf.urls import url, include

from .views import ApiRoot, TeamsList, TeamDetails


urlpatterns = [
    # Api root
    url(r'^$', ApiRoot.as_view(), name='api-root'),

    # Teams api
    url(r'^teams/?$', TeamsList.as_view(), name='teams-list'),
    url(r'^teams/(?P<pk>\d+)/?$', TeamDetails.as_view(),
        name='team-details'),

    # Users api
    url(r'^users/', include('users.urls')),
]
