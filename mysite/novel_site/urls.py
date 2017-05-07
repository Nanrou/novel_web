# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views


app_name = 'novel_site'
urlpatterns = [
    # url(r'^$', views.home, name='home'),
    url(r'^category/(?P<cate>[a-z]+)/$', views.category, name='category'),
    url(r'^book/(?P<pk>[0-9]+)/$', views.InfoView.as_view(), name='info'),
    url(r'^book(?P<pk>[0-9]+>)/(?P<index>[0-9]+)/$', views.detail, name='detail')  # 可以用include

]