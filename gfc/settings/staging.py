import os
import sys


globals().update(vars(sys.modules['gfc.settings']))


SECRET_KEY = os.environ.get('DJANGO_SECRET')

DEBUG = False
TEMPLATE_DEBUG = False

ADMINS = [('Ignat', 'mail@igonato.com')]

ALLOWED_HOSTS = ['dev.goodfoot.club', 'localhost']

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASS')
EMAIL_PORT = 587
