# -*- coding: utf-8 -*-

from .common import *

ALLOWED_HOSTS = [
    '127.0.0.1',
    'superxiaoshuo.dev',
    'm.superxiaoshuo.dev',
]

DEBUG = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'lolololol',
    },
}

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
        INTERNAL_IPS = ['127.0.0.1', '125.89.65.71']
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        )

