"""
WSGI config for mysite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings.prod")

# sys.path.insert(0, '/home/nan/code/novel_web/mysite')

application = get_wsgi_application()
