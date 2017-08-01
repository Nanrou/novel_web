from django.conf.urls import url, include
from . import views


app_name = 'mobile'
urlpatterns = [
    url(r'^$', views.MobileHomeView.as_view(), name='home'),
    url(r'^cate/quanben/$', views.MobileQuanbenView.as_view(), name='quanben'),
    url(r'^cate/(?P<cate>[a-z]+)/$', views.MobileCategoryView.as_view(), name='category'),
    url(r'^info/(?P<pk>[0-9]+)/$', views.MobileInfoView.as_view(), name='info'),
    url(r'^info/(?P<pk>[0-9]+)-(?P<page>[0-9]+)/$', views.MobileInfoPaginatorView.as_view(), name='info'),
    url(r'^book/(?P<pk>[0-9]+)/(?P<index>[0-9]+)/$', views.MobileBookView.as_view(), name='detail'),
    url(r'^search', views.MobileSearchView.as_view(), name='search'),
]
