import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()


from novel_site import models

info = models.InfoTable.objects.get(id=1)
print(info.title)