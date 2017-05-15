# -*- coding:utf-8 -*-

import os, sys

sys.path.append('../mysite/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

try:
    from mysite.novel_site import models
except ImportError:
    from novel_site import models

