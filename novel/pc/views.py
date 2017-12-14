from random import sample

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from django.db.models import Q

from .models import CategoryTable, BookTable, ChapterTable


# Create your views here.

def get_recommend_book():
    book_ids = sample(range(1, BookTable.objects.count()), 10)
    q = Q()
    for book_id in book_ids:
        q.add(Q(**{'id': book_id}), Q.OR)
    return BookTable.objects.filter(q).only('title', 'id')


class HomeView(TemplateView):
    template_name = 'pc/home.html'

    @staticmethod
    def get_variety_book():
        cate_list = []

        for index in range(1, 7):
            books = BookTable.objects.filter(category_id=index) \
                        .select_related('author', 'category').all()[:14] \
                        .only('author', 'category', 'image', 'resume', 'id', 'title')
            cate_list.append(books)
        return cate_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['top_four'] = BookTable.top_four_book()

        cate_list = self.get_variety_book()
        context['cate_list1'] = cate_list[:3]
        context['cate_list2'] = cate_list[3:]

        context['latest_books'] = BookTable.objects.select_related('author', 'category') \
                                           .defer('image', 'resume').order_by('update_time').all()[:20]
        context['newest_books'] = BookTable.objects.select_related('author', 'category') \
                                           .only('author', 'title', 'id', 'category', 'update_time') \
                                           .order_by('-id').all()[:20]
        return context


class CategoryView(DetailView):
    template_name = 'pc/category.html'
    context_object_name = 'cate'
    slug_field = 'cate'
    slug_url_kwarg = 'cate'
    model = CategoryTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['cate_books'] = self.object.cate_books.select_related('author') \
                                    .only('author', 'resume', 'image', 'title', 'id', 'category_id') \
                                    .all()[:6]
        context['latest_books'] = self.object.cate_books \
                                      .select_related('author', 'category') \
                                      .defer('image', 'resume') \
                                      .order_by('update_time').all()[:20]
        context['recommend_books'] = self.object.cate_books \
                                         .select_related('author', 'category') \
                                         .only('author', 'title', 'id', 'category').all()[:20]
        return context


class BookView(DetailView):
    template_name = 'pc/book.html'
    context_object_name = 'book'
    queryset = BookTable.objects.select_related('author', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        all_chapters = list(self.object.all_chapters.only('id', 'title_id', 'book_id', 'chapter'))

        context['all_chapters'] = all_chapters

        if len(all_chapters) < 8:
            context['latest_eight_chapters'] = reversed(all_chapters)
        else:
            context['latest_eight_chapters'] = reversed(all_chapters[-8:])

        context['recommend_books'] = get_recommend_book()
        return context


class ChapterView(DetailView):
    template_name = 'pc/chapter.html'
    model = ChapterTable

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['book'] = BookTable.objects.select_related('category')\
            .only('id', 'title', 'category').get(id=self.kwargs['book_id'])

        context['recommend_books'] = get_recommend_book()
        return context


class QuanbenView(ListView):
    template_name = 'pc/quanben.html'
    context_object_name = 'books'
    queryset = BookTable.objects.select_related('author', 'category') \
        .only('author', 'category', 'id', 'title') \
        .filter(_status=True).order_by('update_time')

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
#     template_name = 'pc/chapter.html'
#     pk_url_kwarg = 'index'
