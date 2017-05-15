# -*- coding:utf-8 -*-

from django.shortcuts import render, loader, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import CategoryTable, InfoTable, BookTableOne, MAP_DICT
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView

# Create your views here.


class HomeView(TemplateView):
    template_name = 'novel_site/home.html'


class CategoryView(TemplateView):
    template_name = 'novel_site/category.html'


class InfoView(DetailView):

    template_name = 'novel_site/info.html'
    # context_object_name = 'all_chapters'

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object(queryset=InfoTable.objects.all())
    #     return super(InfoView, self).get(request, *args, **kwargs)
    def get_queryset(self):
        return InfoTable.objects.select_related()

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)
        all_chapters = list(self.object.all_chapters)
        context['all_chapters'] = all_chapters
        context['latest_chapter'] = all_chapters[-1]
        return context


class BookView(DetailView):

    template_name = 'novel_site/detail.html'
    pk_url_kwarg = 'index'

    def get_adjacent_page(self):  # ??????????
        ll = list(self.all_chapters.only('id', 'book_id'))
        print('-'*20, ll, type(ll))
        index = ll.index(self.object)
        print(index)
        if index - 1 < 0:
            last_page_url = self.book_info.get_absolute_url()
        else:
            last_page_url = ll[index-1].get_absolute_url()
        if index + 1 < len(ll):
            next_page_url = self.del_url_tail(self.object.get_absolute_url()) + str(index+1) + '/'
        else:
            next_page_url = self.book_info.get_absolute_url()
        return last_page_url, next_page_url

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        context['book_info'] = self.book_info
        # context['last_page'], context['next_page'] = self.get_adjacent_page()
        return context

    # def get_object(self):
    #     self.book_info = InfoTable.objects.select_related.get(pk=self.kwargs['pk'])
    #     return self.book_info.all_chapters

    def get_queryset(self):
        self.book_info = InfoTable.objects.defer('resume', 'image', 'update_time', 'status').select_related().get(pk=self.kwargs['pk'])
        self.all_chapters = self.book_info.all_chapters_detail
        return self.all_chapters  # 传给父类的get object，再寻找对应的条目

    @staticmethod
    def del_url_tail(url):
        url = url[:-1]
        while True:
            if url[-1] == '/':
                break
            url = url[:-1]
        return url

