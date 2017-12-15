from django.urls import path
from django.views.decorators.cache import cache_page

from . import views


app_name = 'pc'
urlpatterns = [
    # 主视图
    path('', views.HomeView.as_view(), name='home'),
    path('cate/<str:cate>/', views.CategoryView.as_view(), name='category'),
    path('book/<int:pk>/', views.BookView.as_view(), name='book'),
    path('chapter/<int:book_id>/<int:pk>/', views.ChapterView.as_view(), name='chapter'),
    path('quanben/', views.QuanbenView.as_view(), name='quanben'),

    # 功能视图
    path('search/', views.SearchView.as_view(), name='search'),
    path('upload/', views.upload, name='upload'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('profile/', views.profile, name='profile'),

    # api
    path('refresh_captcha/', views.refresh_captcha, name='captcha'),
    path('logout/', views.logout_handler, name='logout'),
    # path('add_book/<int:pk>/'),
    # path('remove/<int:pk>/'),
]
