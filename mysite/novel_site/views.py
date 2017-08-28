# -*- coding:utf-8 -*-

from random import sample
import logging
import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django_hosts import reverse as host_reverse
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

from .models import CategoryTable, InfoTable
from .form_test import TestForm, TestFormSet
# Create your views here.

logger = logging.getLogger(__name__)


def get_book_from_cate():  # 返回每个分类下的书
    cate_list = []
    # for index in range(1, 6):
    #     books = CategoryTable.objects.filter(id=index)[:1].cate_books.\
    #         select_related('author', 'category').all()[:6].\
    #         only('author', 'category', 'image', 'resume', 'id', 'title')
    # for books in books_list:
    #     cate_list.append([books[0], books])
    for index in range(1, 6):
        books = InfoTable.objects.filter(category_id=index)\
            .select_related('author', 'category').all()[:6]\
            .only('author', 'category', 'image', 'resume', 'id', 'title')
        cate_list.append(books)

    finished_books = InfoTable.objects.filter(_status=1)\
        .select_related('author', 'category').all()[:6] \
        .only('author', 'category', 'image', 'resume', 'id', 'title')

    cate_list.append(finished_books)
    return cate_list


class HomeView(TemplateView):
    template_name = 'novel_site/home.html'

    def get_context_data(self, **kwargs):
        context = dict()
        context['top_four'] = InfoTable.objects.select_related('author').filter(id__lt=5)\
            .only('title', 'author', 'resume', 'image')

        cate_list = get_book_from_cate()
        context['cate_list1'] = cate_list[0:3]
        context['cate_list2'] = cate_list[3:]

        context['latest_books'] = InfoTable.objects.select_related('author', 'category')\
            .only('category', 'author', 'title', 'latest_chapter', 'latest_chapter_url', 'id', 'update_time') \
            .order_by('update_time').all()[:20]

        context['newest_books'] = InfoTable.objects.select_related('category')\
            .only('author', 'title', 'id', 'category', 'update_time')\
            .order_by('-id').all()[:20]

        return context


class CategoryView(DetailView):
    template_name = 'novel_site/category.html'
    context_object_name = 'cate'

    def get_object(self, queryset=None):
        self.object = CategoryTable.objects.get(cate=self.kwargs['cate'])
        return self.object

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['cate_books'] = self.object.cate_books.select_related('author').all()[:6]\
            .only('author', 'resume', 'image', 'title', 'id', 'category_id')
        context['recommend_books'] = self.object.cate_books.select_related('author').all()[:20] \
            .only('author', 'title', 'id', 'category')
        context['latest_books'] = self.object.cate_books.select_related('author')\
            .only('category', 'author', 'title', 'latest_chapter', 'latest_chapter_url', 'id', 'update_time')\
            .order_by('update_time').all()[:20]

        return context


class InfoView(DetailView):

    template_name = 'novel_site/info.html'
    context_object_name = 'book'

    def get_queryset(self):
        return InfoTable.objects.select_related('author', 'category')  # 返回所有的书

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)  # 这里面已经将infotable的get(id=n)赋给self.object了
        all_chapters = list(self.object.all_chapters)
        context['all_chapters'] = all_chapters
        try:
            context['latest_eight_chapters'] = reversed(all_chapters[-8:])
        except IndexError:
            pass
        return context


class BookView(DetailView):

    template_name = 'novel_site/detail.html'
    pk_url_kwarg = 'index'

    def get_adjacent_page(self):  # 这个是通过判断序号是否超出范围来决定前后的url
        paginator = Paginator(self.queryset.order_by('-id'), 1)
        # 注意这个分页函数生产的序号是从1开始的，而我章节的序号不是从1开始的
        try:
            _tmp = paginator.page(self.kwargs['index'].replace(self.kwargs['pk'], '', 1))
        except EmptyPage or PageNotAnInteger:
            _tmp = paginator.page(paginator.num_pages)

        if _tmp.has_next():
            next_page_url = host_reverse('novel_site:detail', host='www',
                                         kwargs={'pk': self.kwargs['pk'], 'index': str(int(self.kwargs['index']) + 1)})
            # next_page_url = reverse('novel_site:detail', kwargs={'pk': self.kwargs['pk'], 'index': str(_tmp.next_page_number())})
        else:
            next_page_url = host_reverse('novel_site:info', host='www', kwargs={'pk': self.kwargs['pk']})
            # next_page_url = reverse('novel_site:info', kwargs={'pk': self.kwargs['pk']})

        if _tmp.has_previous():
            previous_page_url = host_reverse('novel_site:detail', host='www',
                                             kwargs={'pk': self.kwargs['pk'], 'index': str(int(self.kwargs['index']) - 1)})
            # previous_page_url = reverse('novel_site:detail', kwargs={'pk': self.kwargs['pk'], 'index': str(_tmp.next_page_number())})
        else:
            previous_page_url = host_reverse('novel_site:info', host='www', kwargs={'pk': self.kwargs['pk']})
            # previous_page_url = reverse('novel_site:info', kwargs={'pk': self.kwargs['pk']})
        return previous_page_url, next_page_url

    def get_queryset(self):
        self.book_info = InfoTable.objects.select_related('category')\
            .only('title', 'id', 'store_des', 'category_id').get(pk=self.kwargs['pk'])
        self.queryset = self.book_info.all_chapters_detail
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        context['book_info'] = self.book_info
        context['previous_page'], context['next_page'] = self.get_adjacent_page()
        return context


class QuanbenView(ListView):
    template_name = 'novel_site/quanben.html'
    queryset = InfoTable.objects.select_related('author', 'category').filter(_status=True).order_by('update_time')
    context_object_name = 'books'


class SearchView(TemplateView):
    template_name = 'novel_site/search.html'


class SearchTest(TemplateView):
    template_name = 'novel_site/search_api_test.html'


def page_not_found(request):
    return render(request, 'novel_site/404.html')


def form_test(request):
    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            for data in form.cleaned_data:
                logger.info(data)
            return HttpResponseRedirect('/')
        else:
            return render(request, 'novel_site/form_test.html', {'form': form})
    else:
        form = TestForm()
        return render(request, 'novel_site/form_test.html', {'form': form})


def refresh_captcha(request):
    json_content = dict()
    json_content['new_cptch_key'] = CaptchaStore.generate_key()
    json_content['new_cptch_image'] = captcha_image_url(json_content['new_cptch_key'])
    return HttpResponse(json.dumps(json_content), content_type='application/json')
