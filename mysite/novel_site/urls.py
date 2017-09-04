# -*- coding:utf-8 -*-

from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views


app_name = 'novel_site'
urlpatterns = [

    url(r'^$', cache_page(60 * 20)(views.HomeView.as_view()), name='home'),  # 整页缓存，并在view中根据cookie来识别
    url(r'^cate/quanben/$', views.QuanbenView.as_view(), name='quanben'),
    url(r'^cate/(?P<cate>[a-z]+)/$', views.CategoryView.as_view(), name='category'),  # 在模版文件用标签缓存
    url(r'^info/(?P<pk>[0-9]+)/$', views.InfoView.as_view(), name='info'),  # 在视图文件用cache的api缓存
    url(r'^book/(?P<pk>[0-9]+)/(?P<index>[0-9]+)/$', views.BookView.as_view(), name='detail'),  # 检验头部的last-modified

    
    url(r'^search', views.SearchView.as_view(), name='search'),
    url(r'^upload', views.form_test, name='form_test'),
    url(r'^signup/$', views.sign_up, name='sign_up'),
    url(r'^signin/$', views.sign_in, name='sign_in'),
    url(r'^profile', views.show_profile),
    # api
    url(r'^refresh_captcha', views.refresh_captcha),
    url(r'^logout', views.logout_view),
    url(r'^add_book/(?P<book_id>[0-9]+)/$', views.add_book),
    url(r'^remove_book/(?P<book_id>[0-9]+)/$', views.remove_book),
    url(r'^test/$', views.just_test),
]

