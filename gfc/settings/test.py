from .base import *


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gfc_test',
        'USER': 'gfc',
        'PASSWORD': 'gfc',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {},
    'loggers': {},
}
