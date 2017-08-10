from .common import *


DEBUG = False

ALLOWED_HOSTS = [
        '127.0.0.1',
        'superxiaoshuo.com',
        'www.superxiaoshuo.com',
        'm.superxiaoshuo.com',
        ]


# Application definition

INSTALLED_APPS.append('gunicorn')

MIDDLEWARE = (
    ['django.middleware.cache.UpdateCacheMiddleware'] +
    MIDDLEWARE +
    ['django.middleware.cache.FetchFromCacheMiddleware']
)

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Caches

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PICKLE_VERSION": -1,
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

# Loggers

# LOGGING["handlers"]["syslog"] = {
#     "formatter": "full",
#     "level": "DEBUG",
#     "class": "logging.handlers.SysLogHandler",
#     "address": "/dev/log",
#     "facility": "local4",
# }

LOGGING["loggers"]["django.request"]["handlers"].append("syslog")

# django-host settings

PARENT_HOST = 'superxiaoshuo.com'

