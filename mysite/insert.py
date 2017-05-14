import os

from django.conf import settings
# from mysite.mysite import settings as setting
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
# # settings.configure(default_settings=setting)
django.setup()

from novel_site import models
#
info = models.InfoTable.objects.get(id=1)
print(info.title)
