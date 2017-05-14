import os
from django.conf import Settings
from mysite.mysite import settings as setting

# settings.configure()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.mysite.settings')
# Settings(settings_module='mysite.mysite.settings')

import django
django.setup()

from mysite.novel_site import models