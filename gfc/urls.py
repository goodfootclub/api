"""gfc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from djoser.views import (
    ActivationView,
    PasswordResetConfirmView,
    PasswordResetView,
    RegistrationView,

)
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/auth/jwt/$', obtain_jwt_token),
    url(r'^api/auth/jwt/refresh/$', refresh_jwt_token),
    url(r'^api/auth/jwt/verify/$', verify_jwt_token),

    url(r'^api/auth/register/$', RegistrationView.as_view()),
    url(r'^api/auth/activate/$', ActivationView.as_view()),
    url(r'^api/auth/password/reset/$', PasswordResetView.as_view()),
    url(
        r'^api/auth/password/reset/confirm/$',
        PasswordResetConfirmView.as_view()
    ),
    url(
        r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),
    url(r'^auth/', include('social_django.urls', namespace='social')),
    url(r'^django-auth/', include('django.contrib.auth.urls')),
    url(r'^api/', include('main.urls'))
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
