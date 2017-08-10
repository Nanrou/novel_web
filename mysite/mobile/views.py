from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect, render
from django.views.decorators.cache import cache_page
# from django_hosts.resolvers import reverse

from novel_site.views import CategoryView, InfoView, BookView
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

    # def get_context_data(self, **kwargs):
    #     return {'cate_books': self.obj.cate_books.all()[:10]}


class MobileInfoView(InfoView):
    template_name = 'mobile/info.html'
    context_object_name = 'info'

    def get_context_data(self, **kwargs):
        context = super(MobileInfoView, self).get_context_data(**kwargs)
        context['first_chapter'] = context['all_chapters'][0]
        return context


@cache_page(60 * 120)
def info_paginator(request, pk, page):
    template_name = 'mobile/info_paginator.html'

    # pk = request.GET.get('pk')
    # page = request.GET.get('page')
    try:
        pk = int(pk)
        page = int(page)
    except ValueError:
        redirect('/')

    info = InfoTable.objects.select_related('author').only('id', 'store_des', 'title','author_id').get(id=pk)
    all_chapters = info.all_chapters.order_by('id')
    paginator = Paginator(all_chapters, 20)
    if page > paginator.num_pages:
        return redirect(reverse('mobile:info_paginator', kwargs={'pk': pk, 'page': paginator.num_pages}))
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        return redirect(reverse('mobile:info_paginator', kwargs={'pk': pk, 'page': 1}))
    except EmptyPage:
        return redirect(reverse('mobile:info_paginator', kwargs={'pk': pk, 'page': page}))
    return render(request, template_name, {'info': info, 'contacts': contacts})


class MobileBookView(BookView):
    template_name = 'mobile/detail.html'
    pk_url_kwarg = 'index'
    context_object_name = 'book'

    # def get_queryset(self):
    #     shili = InfoTable.objects.get(pk=self.kwargs['pk'])
    #     self.mulu_url = shili.get_mobile_url()
    #     self.queryset = shili.all_chapters_detail
    #     return self.queryset

    def get_queryset(self):
        self.book_info = InfoTable.objects.only('title', 'id', 'store_des').get(pk=self.kwargs['pk'])
        self.queryset = self.book_info.all_chapters_detail
        return self.queryset

    # def get_context_data(self, **kwargs):
    #     context = super(MobileBookView, self).get_context_data(**kwargs)
    #     context['last_page'], context['next_page'] = self.get_adjacent_page()
    #     context['mulu'] = self.mulu_url
    #     return context


class MobileSearchView(TemplateView):
    template_name = 'mobile/search.html'


def page_not_found(request):
    return render(request, 'mobile/404.html')
