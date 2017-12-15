# -*- coding: utf-8 -*-

from .common import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#1z2ng)dpkfkhvu=g_t$$i$8+#%-0(d00gd!w7tsp$65h8fb$i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = [
    '127.0.0.1',
    'superxiaoshuo.dev',
    'm.superxiaoshuo.dev',
    'www.superxiaoshuo.dev'
]


# Cache Settings

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    },
}


# DB timeout

CONN_MAX_AGE = 300

# Session

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CSRF_COOKIE_SECURE = False

# django-hosts settings

PARENT_HOST = 'superxiaoshuo.dev:8000'

# 邀请码

INVITE_CODE = ['lulu', 'Amao']

if DEBUG:
    try:
        import debug_toolbar
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
