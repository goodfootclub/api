import os
import sys


globals().update(vars(sys.modules['gfc.settings']))


SECRET_KEY = os.environ.get('DJANGO_SECRET')

DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['dev.goodfoot.club', 'localhost']

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_PASS')
EMAIL_PORT = 587

RAVEN_CONFIG = {
    'dsn':
        'https://414e5d642b304b019e2638cd0e2d3db1:e0943ce5eefa492fa68222'
        '64ae73746a@sentry.io/201630',
    'release': raven.fetch_git_sha(APP_DIR),
}
