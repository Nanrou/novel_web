from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
                         host(r'', settings.ROOT_URLCONF, name='www', scheme='http'),
                         host(r'm', 'mysite.mobile', name='mobile', scheme='http')
                         )
