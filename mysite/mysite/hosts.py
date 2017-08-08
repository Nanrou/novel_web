from django.conf import settings
from django_hosts import patterns, host

if not settings.DEBUG:
    host_patterns = patterns('',
                             host(r'www', settings.ROOT_URLCONF, name='www', scheme='http'),
                             host(r'm', 'mysite.mobile', name='mobile', scheme='http')
                             )
else:
    host_patterns = patterns('',
                             host(r'www', settings.ROOT_URLCONF, name='www', scheme='http'),
                             )
