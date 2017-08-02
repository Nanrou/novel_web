from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from novel_site.views import CategoryView, InfoView

from novel_site.views import get_book_from_cate
from novel_site.models import InfoTable
# Create your views here.


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
            all_chapters = self.object.all_chapters.order_by('-id')
            context['all_chapters'] = all_chapters[:12]
            context['latest_chapter'] = all_chapters[0]
        except IndexError:
            pass
        return context


class MobileInfoPaginatorView(InfoView):
    template_name = 'mobile/info_paginator.html'
    context_object_name = 'info'

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)

        all_chapters = self.object.all_chapters.order_by('id')
        page = self.kwargs['page']
        paginator = Paginator(all_chapters, 20)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        except EmptyPage:
            contacts = paginator.page(paginator.num_pages)

        context['contacts'] = contacts
        context['num_pages'] = paginator.num_pages
        return context


class MobileBookView(DetailView):
    template_name = 'mobile/detail.html'
    pk_url_kwarg = 'index'
    context_object_name = 'book'

    def get_adjacent_page(self):  # 这里是直接构造前后的url，然后回db里判断是否存在
        try:
            index = int(self.kwargs['index'])
            if self.queryset.filter(pk=index-1).exists():
                last_page_url = reverse('mobile:detail', kwargs={'pk': self.kwargs['pk'], 'index': str(index-1)})
            else:
                last_page_url = self.mulu_url
            if self.queryset.filter(pk=index+1).exists():
                next_page_url = reverse('mobile:detail', kwargs={'pk': self.kwargs['pk'], 'index': str(index+1)})
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


class MobileSearchView(TemplateView):
    template_name = 'mobile/search.html'
