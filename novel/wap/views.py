from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

try:
    from novel.pc.models import BookTable, CategoryTable, ChapterTable
    from novel.pc.views import get_recommend_book
except ModuleNotFoundError:
    from pc.models import BookTable, CategoryTable, ChapterTable
    from pc.views import get_recommend_book


# Create your views here.


class HomeView(TemplateView):
    template_name = 'wap/home.html'

    @staticmethod
    def get_variety_book():
        cate_list = []

        for index in range(1, 7):
            books = BookTable.objects.filter(category_id=index) \
                        .select_related('author', 'category').all()[:7] \
                .only('author', 'category', 'image', 'resume', 'id', 'title')
            cate_list.append(books)
        return cate_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['cate_book'] = self.get_variety_book()
        return context


class CategoryView(ListView):
    template_name = 'wap/category.html'
    paginate_by = 10
    context_object_name = 'cate_books'

    def get_queryset(self):
        return CategoryTable.objects.get(cate=self.kwargs['cate']).cate_books.select_related('author').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['cate'] = CategoryTable.objects.get(cate=self.kwargs['cate'])
        return context


class BookView(DetailView):
    template_name = 'wap/book.html'
    context_object_name = 'book'
    queryset = BookTable.objects.select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['first_chapter'] = self.object.all_chapters.only('id', 'title_id', 'book_id', 'chapter').first()
        context['latest_eight_chapters'] = self.object.all_chapters.only('id', 'title_id', 'book_id', 'chapter') \
                                               .order_by('-id').all()[:12]
        return context


class PaginatorView(ListView):
    template_name = 'wap/book_paginator.html'
    paginate_by = 20
    context_object_name = 'chapters'

    def get_queryset(self):
        return BookTable.objects.get(id=self.kwargs['pk']) \
            .all_chapters.only('id', 'title_id', 'book_id', 'chapter').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['url'] = BookTable.objects.get(id=self.kwargs['pk']).get_mobile_url()
        return context


class ChapterView(DetailView):
    template_name = 'wap/chapter.html'
    model = ChapterTable
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['book_info'] = BookTable.objects.only('id', 'title').get(id=self.kwargs['book_id'])
        context['recommend_books'] = get_recommend_book()
        return context


class QuanbenView(ListView):
    template_name = 'wap/quanben.html'
    queryset = BookTable.objects.select_related('author', 'category').filter(_status=1).all()
    paginate_by = 10
    context_object_name = 'books'


def page_not_found(request):
    return render(request, 'wap/404.html')


def page_forbidden(request):
    return render(request, 'wap/403.html')


def server_wrong(request):
    return render(request, 'wap/502.html')
