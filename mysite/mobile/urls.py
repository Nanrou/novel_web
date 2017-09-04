# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views
from novel_site.views import (sign_in, sign_up, show_profile,
                              refresh_captcha, logout_view, add_book, remove_book)

app_name = 'mobile'
# urlpatterns = [
#     url(r'^$', cache_page(60 * 30)(views.MobileHomeView.as_view()), name='home'),
#     url(r'^cate/quanben/$', views.MobileQuanbenView.as_view(), name='quanben'),
#     url(r'^cate/(?P<cate>[a-z]+)/$', cache_page(60 * 60)(views.MobileCategoryView.as_view()), name='category'),
#     url(r'^cate/(?P<cate>[a-z]+)-(?P<page>[0-9]+)/$', cache_page(60 * 60)(views.MobileCategoryView.as_view()), name='category'),
#     url(r'^info/(?P<pk>[0-9]+)/$', cache_page(60 * 120)(views.MobileInfoView.as_view()), name='info'),
#     url(r'^info/(?P<pk>[0-9]+)-(?P<page>[0-9]+)/$', views.info_paginator, name='info_paginator'),
#     url(r'^book/(?P<pk>[0-9]+)/(?P<index>[0-9]+)/$', views.MobileBookView.as_view(), name='detail'),
#     url(r'^search', views.MobileSearchView.as_view(), name='search'),
#
#     url(r'^signup/$', sign_up, {'pattern': 'moblie'}, name='sign_up'),
#     url(r'^signin/$', sign_in, {'pattern': 'moblie'}, name='sign_in'),
#     url(r'^profile', show_profile, {'pattern': 'moblie'}),
#
# ]

urlpatterns = [
    url(r'^$', views.MobileHomeView.as_view(), name='home'),
    url(r'^cate/quanben/$', views.MobileQuanbenView.as_view(), name='quanben'),
    url(r'^cate/(?P<cate>[a-z]+)/$', views.MobileCategoryView.as_view(), name='category'),
    url(r'^info/(?P<pk>[0-9]+)/$', views.MobileInfoView.as_view(), name='info'),
    url(r'^info/(?P<pk>[0-9]+)-(?P<page>[0-9]+)/$', views.info_paginator, name='info_paginator'),
    url(r'^book/(?P<pk>[0-9]+)/(?P<index>[0-9]+)/$', views.MobileBookView.as_view(), name='detail'),
    url(r'^search', views.MobileSearchView.as_view(), name='search'),

    url(r'^signup/$', sign_up, {'pattern': 'moblie'}, name='sign_up'),
    url(r'^signin/$', sign_in, {'pattern': 'moblie'}, name='sign_in'),
    url(r'^profile', show_profile, {'pattern': 'moblie'}),

    # api
    url(r'^refresh_captcha', refresh_captcha),
    url(r'^logout', logout_view),
    url(r'^add_book/(?P<book_id>[0-9]+)/$', add_book),
    url(r'^remove_book/(?P<book_id>[0-9]+)/$', remove_book),
]
