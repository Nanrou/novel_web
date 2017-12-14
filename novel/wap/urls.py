from django.urls import path
from django.views.decorators.cache import cache_page

from . import views


app_name = 'wap'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('cate/<str:cate>/', views.CategoryView.as_view(), name='category'),
    path('cate/<str:cate>/page-<int:page>/', views.CategoryView.as_view(), name='category_paginator'),
    path('book/<int:pk>/', views.BookView.as_view(), name='book'),
    path('book/<int:pk>/page-<int:page>/', views.PaginatorView.as_view(), name='book_paginator'),
    path('chapter/<int:book_id>/<int:pk>/', views.ChapterView.as_view(), name='chapter'),
    path('quanben/', views.QuanbenView.as_view(), name='quanben'),
]
