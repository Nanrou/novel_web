from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
                         host(r'www', settings.ROOT_URLCONF, name='www',),
                         host(r'm', 'mysite.urls.mobile', name='mobile',)
                         )
