# -*- coding:utf-8 -*-

from random import sample
from django.shortcuts import render
from django.urls import reverse
from .models import CategoryTable, InfoTable
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView

# Create your views here.


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
        context['top_four'] = \
            InfoTable.objects.select_related('author').filter(id__lt=5).only('title', 'author', 'resume', 'image')

        cate_list = get_book_from_cate()
        context['cate_list1'] = cate_list[0:3]
        context['cate_list2'] = cate_list[3:]

        return context


class CategoryView(DetailView):
    template_name = 'novel_site/category.html'
    context_object_name = 'cate'

    def get_object(self, queryset=None):
        self.obj = CategoryTable.objects.get(cate=self.kwargs['cate'])
        return self.obj

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['cate_books'] = self.obj.cate_books.all()[:5]
        return context


class InfoView(DetailView):

    template_name = 'novel_site/info.html'
    # context_object_name = 'all_chapters'

    # def get(self, request, *args, **kwargs):
    #     self.object = self.get_object(queryset=InfoTable.objects.all())
    #     return super(InfoView, self).get(request, *args, **kwargs)
    def get_queryset(self):
        return InfoTable.objects.select_related()  # 返回所有的书

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)  # 这里面已经将infotable的get(id=n)赋给self.object了
        all_chapters = list(self.object.all_chapters)
        context['all_chapters'] = all_chapters
        try:
            context['latest_chapter'] = all_chapters[-1]
            context['latest_ten_chapters'] = reversed(all_chapters[-8:])
        except IndexError:
            pass
        return context


class BookView(DetailView):

    template_name = 'novel_site/detail.html'
    pk_url_kwarg = 'index'

    def get_adjacent_page(self):  # 这个是通过判断序号是否超出范围来决定前后的url
        ll = list(self.book_info.all_chapters_id_only)  # 这里是通过找所有的id来判断是否有前后
        index = ll.index(self.object)
        if index - 1 < 0:
            last_page_url = self.book_info.get_absolute_url()
        else:
            last_page_url = ll[index-1].get_absolute_url()
        if index + 1 < len(ll):
            next_page_url = ll[index+1].get_absolute_url()
        else:
            next_page_url = self.book_info.get_absolute_url()
        return last_page_url, next_page_url

# 可以通过直接构造前后的id来判断，若找不到就返回首页

    def get_queryset(self):
        self.book_info = InfoTable.objects.defer('resume', 'image', 'update_time', '_status').select_related().get(pk=self.kwargs['pk'])
        return self.book_info.all_chapters_detail  # 传给父类的get object，再寻找对应的条目

    def get_context_data(self, **kwargs):
        context = super(BookView, self).get_context_data(**kwargs)
        context['book_info'] = self.book_info
        context['last_page'], context['next_page'] = self.get_adjacent_page()
        return context


class QuanbenView(ListView):

    template_name = 'novel_site/quanben.html'
    queryset = InfoTable.objects.filter(_status=True).order_by('update_time')
    context_object_name = 'books'


class MobileHomeView(TemplateView):
    template_name = 'mobile/home.html'

    def get_context_data(self, **kwargs):
        # context = super(MobileHomeView, self).get_context_data(**kwargs)
        # context['cate_book'] = get_book_from_cate()
        # return context
        return {'cate_book': get_book_from_cate()}


class MobileQuanbenView(TemplateView):  # unfinished
    template_name = 'mobile/quanben.html'


class MobileCategoryView(CategoryView):
    template_name = 'mobile/category.html'

    def get_context_data(self, **kwargs):
        return {'cate_books': self.obj.cate_books.all()[:10]}


class MobileInfoView(InfoView):
    template_name = 'mobile/info.html'
    context_object_name = 'info'

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)
        try:
            all_chapters = self.object.all_chapters.order_by('-id')[:12]
            context['all_chapters'] = all_chapters
            context['latest_chapter'] = all_chapters[0]
        except IndexError:
            pass
        return context


class MobileBookView(DetailView):
    template_name = 'mobile/detail.html'
    pk_url_kwarg = 'index'
    context_object_name = 'book'

    def get_adjacent_page(self):  # 这里是直接构造前后的url，然后回db里判断是否存在
        try:
            index = int(self.kwargs['index'])
            if self.queryset.filter(pk=index-1).exists():
                last_page_url = reverse('novel_site:m_detail', kwargs={'pk': self.kwargs['pk'], 'index': str(index-1)})
            else:
                last_page_url = self.mulu_url
            if self.queryset.filter(pk=index+1).exists():
                next_page_url = reverse('novel_site:m_detail', kwargs={'pk': self.kwargs['pk'], 'index': str(index+1)})
            else:
                next_page_url = self.mulu_url
            return last_page_url, next_page_url
        except TypeError:
            pass

    def get_queryset(self):
        shili = InfoTable.objects.get(pk=self.kwargs['pk'])
        self.mulu_url = shili.get_mobile_url()
        self.queryset = shili.all_chapters_detail
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(MobileBookView, self).get_context_data(**kwargs)
        context['last_page'], context['next_page'] = self.get_adjacent_page()
        context['mulu'] = self.mulu_url
        return context


class SearchView(TemplateView):
    template_name = 'novel_site/search.html'


class SearchTest(TemplateView):
    template_name = 'novel_site/search_api_test.html'


def page_not_found(request):
    return render(request, 'novel_site/404.html')

