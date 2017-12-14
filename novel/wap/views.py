from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

# from ..pc.models import CategoryTable


# Create your views here.


class HomeView(TemplateView):
    template_name = 'wap/home.html'


class CategoryView(TemplateView):
    template_name = 'wap/category.html'


class BookView(TemplateView):
    template_name = 'wap/book.html'


class ChapterView(TemplateView):
    template_name = 'wap/chapter.html'


class QuanbenView(TemplateView):
    template_name = 'wap/quanben.html'

# class CategoryView(DetailView):
#     template_name = 'pc/category.html'
#     context_object_name = 'cate'
#
#     slug_url_kwarg = 'cate'
#     slug_field = 'cate'
#     model = CategoryTable

# class BookView(DetailView):
#     template_name = 'pc/book.html'
#     context_object_name = 'book'
#
#
# class ChapterView(DetailView):
#     template_name = 'pc/detail.html'
#     pk_url_kwarg = 'index'

