import os
import sys


globals().update(vars(sys.modules['settings']))


SECRET_KEY = os.environ.get('DJANGO_SECRET')

DEBUG = False

ALLOWED_HOSTS = ['goodfoot.club']

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('FB_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('FB_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = [
    'email',
    # 'user_birthday',  # TODO: Needs approval from Facebook
]

EMAIL_SUBJECT_PREFIX = '[Good Foot Club] '
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASS')
EMAIL_PORT = 587
