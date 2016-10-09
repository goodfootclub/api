from django.conf.urls import url

from .views import ApiRoot


urlpatterns = [
    # Api root
    url(r'^$', ApiRoot.as_view(), name='api-root'),
]
