import os
from random import SystemRandom
from string import ascii_letters, digits, punctuation

from .common import *


SECRET_KEY = os.environ.get('SECRET_KEY') or 'bbb'
if not SECRET_KEY:
    _secret = os.path.join(BASE_DIR, 'no_follow')
    if not os.path.exists(_secret):
        chars = ascii_letters + digits + punctuation
        _secret_key = ''.join(SystemRandom().choice(chars) for _ in range(50))
        with open(_secret, 'w') as wf:
            wf.write(_secret_key)
    else:
        with open(_secret, 'r') as rf:
            _secret_key = rf.read().strip()
    SECRET_KEY = _secret_key


DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'superxiaoshuo.com',
    'm.superxiaoshuo.com',
    'www.superxiaoshuo.com'
]

INSTALLED_APPS.append('gunicorn')

# Cache Settings

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

# 直接做整站缓存了
MIDDLEWARE.insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
MIDDLEWARE.append('django.middleware.cache.FetchFromCacheMiddleware')

# django-hosts settings

PARENT_HOST = 'superxiaoshuo.com'

# captcha settings

CAPTCHA_LENGTH = 5

# 邀请码

INVITE_CODE = os.environ.get('INVITE_CODE') or []
