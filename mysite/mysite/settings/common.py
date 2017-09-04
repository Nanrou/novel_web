# -*- coding:utf-8 -*-

import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Log path

LOGGER_PATH = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'site_log')

if not os.path.exists(LOGGER_PATH):
    os.mkdir(LOGGER_PATH)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#qmln%+&shyq5*h*3flkg5&gn72*f5uxg2+tdm8c=!q@i*$!h2'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Application definition

ROOT_URLCONF = 'mysite.urls.www'

INSTALLED_APPS = [
    'novel_site',
    'mobile',

    'django_hosts',
    'captcha',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
]

# Sites framework settings
SITE_ID = 1

# Common settings
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = False

USE_L10N = False

USE_TZ = False


MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    # 'django.middleware.http.ConditionalGetMiddleware',  # 检查请求头的ETag和Last-modified，并在响应头加上ETag

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'middleware.my_middleware.MobileMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Caches

CACHE_MIDDLEWARE_SECONDS = 60 * 5

CACHE_MIDDLEWARE_KEY_PREFIX = 'site'

# Session
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# django-host settings

ROOT_HOSTCONF = 'mysite.hosts'

DEFAULT_HOST = 'www'

HOST_SCHEME = 'http'

HOST_SITE_TIMEOUT = 3600

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Logger settings

LOGGING = {
    'version': 1,
    # 'disable_existing_loggers': True,

    "formatters": {
        "simple": {"format": "[%(name)s] %(levelname)s: %(message)s"},
        "full": {"format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s"},
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },

    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },

        'default': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGGER_PATH, 'site.log'),
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'formatter': 'full',
            },

        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },

    },

    'loggers': {
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        # },
        'django': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False,
        },
        "django.request": {
            "handlers": ['default'],
            "level": "ERROR",
            "propagate": False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

# Captcha settings

CAPTCHA_TIMEOUT = 1
CAPTCHA_LENGTH = 1
