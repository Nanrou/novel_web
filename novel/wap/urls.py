from django.urls import path
from django.views.decorators.cache import cache_page

from . import views


app_name = 'wap'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),  # 整页缓存，并在view中根据cookie来识别
    path('cate/<str:cate>/', views.CategoryView.as_view(), name='category'),
    path('book/<int:pk>/', views.BookView.as_view(), name='book'),
    path('chapter/<int:pk>/', views.ChapterView.as_view(), name='chapter'),
    path('quanben/', views.QuanbenView.as_view(), name='quanben'),
]
