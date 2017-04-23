"""
Django settings for gfc project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

from os.path import abspath, dirname, join as join_path
from datetime import timedelta

# Build paths inside the project like this: join_path(BASE_DIR, ...)
APP_DIR = dirname(dirname(dirname(abspath(__file__))))
SRV_DIR = dirname(APP_DIR)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r2s57nn3yg8%=h@xwtpy!9k%2opkw&v=3lm=yh9voetblt#v!b'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # 3rd party
    'crispy_forms',
    'rest_framework',
    'social.apps.django_app.default',
    'timezone_field',

    # Ours
    'main',
    'users',
    'games',
    'teams',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gfc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gfc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gfc',
        'USER': 'gfc',
        'PASSWORD': 'gfc',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


# Authentication

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_FACEBOOK_KEY = '1813792338896743'
SOCIAL_AUTH_FACEBOOK_SECRET = '531c95442b081266a13ccbac73935a0a'
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'user_birthday']

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'

SOCIAL_AUTH_PIPELINE = (
    # https://python-social-auth.readthedocs.io/en/latest/pipeline.html
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    # Send a validation email to the user to verify its email address.
    # 'social.pipeline.mail.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',

    # Get extra details from facebook
    'users.pipeline.facebook_extra_details',
)

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(days=60),
    'JWT_ALLOW_REFRESH': True,
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = join_path(SRV_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = join_path(SRV_DIR, 'media')


# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'django-debug.log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join_path(SRV_DIR, 'logs', 'django-debug.log'),
        },
        'app-debug.log': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join_path(SRV_DIR, 'logs', 'app-debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django-debug.log'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'app': {
            'handlers': ['app-debug.log'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Emails

EMAIL_SUBJECT_PREFIX = '[Good Foot Club (DEVELOPMENT)] '


# ReST framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50
}
