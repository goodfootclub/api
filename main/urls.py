from django.conf import settings
from django.conf.urls import url, include
from rest_framework_swagger.views import get_swagger_view
from rest_framework.documentation import include_docs_urls

from .views import ApiRoot, ApiError


urlpatterns = [
    # Api root
    url(r'^$', get_swagger_view(title=settings.API_TITLE)),
    url(r'^error/$', ApiError.as_view(), name='api-error'),
    url(r'^docs/', include_docs_urls(title=settings.API_TITLE)),
    url(r'^users/', include('users.urls')),
    url(r'^', include('teams.urls')),
    url(r'^', include('games.urls')),
]
