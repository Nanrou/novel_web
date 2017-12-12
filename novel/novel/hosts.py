from django_hosts import patterns, host

host_patterns = patterns('',
                         host(r'www', 'novel.urls.url_pc', name='pc',),
                         host(r'm', 'novel.urls.url_wap', name='wap',)
                         )
