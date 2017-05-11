# -*- coding:utf-8 -*-

from django.shortcuts import render, loader, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import CategoryTable, InfoTable, BookTableOne
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
import csv
# Create your views here.


class HomeView(TemplateView):
    template_name = 'novel_site/home.html'


class CategoryView(TemplateView):
    template_name = 'novel_site/category.html'


# class InfoView(DetailView):
#
#     model = InfoTable
#     template_name = 'novel_site/info.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(InfoView, self).get_context_data(**kwargs)
#         return context


class InfoView(ListView):

    # model = InfoTable
    template_name = 'novel_site/info.html'
    context_object_name = 'all_chapters'

    def get_queryset(self):
        self.object = InfoTable.objects.select_related().get(pk=self.kwargs['pk'])
        return self.object.all_chapters

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)
        context['object'] = self.object
        context['latest_chapter'] = self.object_list.last()
        return context


class BookView(DetailView):

    template_name = 'novel_site/detail.html'
    pk_url_kwarg = 'index'

    def next_page(self):
        try:
            return self.book_info.all_chapters.filter(id__lt=self.kwargs['index'])[0].get_absolute_url()
        except IndexError:
            return self.book_info.get_absolute_url

    def last_page(self):
        try:
            return self.book_info.all_chapters.filter(id__gt=self.kwargs['index'])[0].get_absolute_url()
        except IndexError:
            return self.book_info.get_absolute_url

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        context['next_page'] = self.next_page()
        context['last_page'] = self.last_page()
        return context

    # def get(self, request, *args, **kwargs):
    #     self.book_info = InfoTable.objects.get(pk=self.kwargs['pk'])
    #     return super(BookView, self).get(request, *args, **kwargs)
    #
    # def get_object(self, queryset=None):
    #     self.object = self.book_info.all_chapters.get(pk=self.kwargs['index'])
    #     return self.object

    def get_queryset(self):
        self.book_info = InfoTable.objects.get(pk=self.kwargs['pk'])
        return self.book_info.all_chapters



    # def get_queryset(self):
    #     chapters = InfoTable.objects.get(pk=self.kwargs['pk']).all_chapters
    #     chapter = chapters.get(pk=self.kwargs['index'])
    #     print(type(chapters), type(chapter))
    #     return chapters


