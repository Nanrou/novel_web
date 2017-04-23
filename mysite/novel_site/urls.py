# -*- coding:utf-8 -*-

from django.conf.urls import url
from . import views


app_name = 'novel_site'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.detail, name='detail'),

]