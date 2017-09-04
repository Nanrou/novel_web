"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.sitemaps.views import sitemap

from .novel_sitemaps import NovelSitemap
from django.views.decorators.cache import cache_page


sitemaps = {
    'static': NovelSitemap,
}

urlpatterns = [
    url(r'', include('mobile.urls', namespace='mobile')),
    url(r'^sitemap\.xml$', cache_page(86400)(sitemap),
        {
            'sitemaps': sitemaps,
            'template_name': 'mobile/sitemap.xml',
        }, name='sitemap'),
]

handler404 = 'mobile.views.page_not_found'
handler403 = 'mobile.views.forbidden'

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
