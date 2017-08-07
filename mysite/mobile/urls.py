# -*- coding:utf-8 -*-

from django.conf.urls import url, include
from django.views.decorators.cache import cache_page
from . import views


app_name = 'mobile'
urlpatterns = [
    url(r'^$', cache_page(60 * 30)(views.MobileHomeView.as_view()), name='home'),
    url(r'^cate/quanben/$', views.MobileQuanbenView.as_view(), name='quanben'),
    url(r'^cate/(?P<cate>[a-z]+)/$', cache_page(60 * 60)(views.MobileCategoryView.as_view()), name='category'),
    url(r'^info/(?P<pk>[0-9]+)/$', cache_page(60 * 120)(views.MobileInfoView.as_view()), name='info'),
    # url(r'^info/(?P<pk>[0-9]+)-(?P<page>[0-9]+)/$', cache_page(60 * 30)(views.MobileInfoPaginatorView.as_view()), name='info_paginator'),
    url(r'^info/(?P<pk>[0-9]+)-(?P<page>[0-9]+)/$', views.info_paginator, name='info_paginator'),
    url(r'^book/(?P<pk>[0-9]+)/(?P<index>[0-9]+)/$', views.MobileBookView.as_view(), name='detail'),
    url(r'^search', views.MobileSearchView.as_view(), name='search'),
    url(r'^bbb', views.page_not_found, name='404'),
]

