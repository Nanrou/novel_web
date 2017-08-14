# -*- coding: utf-8 -*-

from .common import *

ALLOWED_HOSTS = [
    '127.0.0.1',
    'superxiaoshuo.dev',
    'm.superxiaoshuo.dev',
    'www.superxiaoshuo.dev'
]


# sites framework settings
INSTALLED_APPS.append('django.contrib.sites')
SITE_ID = 1

# sitemaps settings
INSTALLED_APPS.append('django.contrib.sitemaps')

DEBUG = True

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'lolololol',
#     },
# }

CSRF_COOKIE_SECURE = False

# django-hosts settings

PARENT_HOST = 'superxiaoshuo.dev:8000'


if DEBUG:
    try:
        import debug_toolbar  # NOQA
    except ImportError:
        pass
    else:
        DEBUG_TOOLBAR_CONFIG = {
            'JQUERY_URL': r"http://code.jquery.com/jquery-2.1.1.min.js",
        }
        INSTALLED_APPS.append('debug_toolbar')
        INTERNAL_IPS = ['127.0.0.1']
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        )

