from django.conf import settings
from django_hosts import patterns, host

if not settings.DEBUG:
    host_patterns = patterns('',
                             host(r'www', settings.ROOT_URLCONF, name='www',),
                             host(r'm', 'mysite.mobile', name='mobile',)
                             )
else:
    host_patterns = patterns('',
                             host(r'www', settings.ROOT_URLCONF, name='www',),
                             )
