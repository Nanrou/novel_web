from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

try:
    from novel.pc.views import upload, profile, sign_in, sign_up, refresh_captcha, logout_handler
except ModuleNotFoundError:
    from pc.views import upload, profile, sign_in, sign_up, refresh_captcha, logout_handler

app_name = 'wap'
urlpatterns = [
    # 主视图
    path('', views.HomeView.as_view(), name='home'),
    path('cate/<str:cate>/', views.CategoryView.as_view(), name='category'),
    path('cate/<str:cate>/page-<int:page>/', views.CategoryView.as_view(), name='category_paginator'),
    path('book/<int:pk>/', views.BookView.as_view(), name='book'),
    path('book/<int:pk>/page-<int:page>/', views.PaginatorView.as_view(), name='book_paginator'),
    path('chapter/<int:book_id>/<int:pk>/', views.ChapterView.as_view(), name='chapter'),
    path('quanben/', views.QuanbenView.as_view(), name='quanben'),
    path('quanben/page-<int:page>/', views.QuanbenView.as_view(), name='quanben_paginator'),

    # 功能视图
    # path('search/', SearchView.as_view(), name='search'),
    path('upload/', upload, name='upload'),
    path('sign_up/', sign_up, name='sign_up'),
    path('sign_in/', sign_in, name='sign_in'),
    path('profile/', profile, name='profile'),

    # api
    path('refresh_captcha/', refresh_captcha, name='captcha'),
    path('logout/', logout_handler, name='logout'),
]
