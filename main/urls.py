from django.conf.urls import url, include

from .views import ApiRoot


urlpatterns = [
    # Api root
    url(r'^$', ApiRoot.as_view(), name='api-root'),

    # Users api
    url(r'^users/', include('users.urls')),
]
