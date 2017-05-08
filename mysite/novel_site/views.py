# -*- coding:utf-8 -*-

from django.shortcuts import render, loader, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import CategoryTable, InfoTable, BookTableOne
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView

# Create your views here.


def category(request, pk):
    pass


# class InfoView(DetailView):
#
#     model = InfoTable
#     template_name = 'novel_site/info.html'
#
#     def get(self, request, *args, **kwargs):
#
#     # def get_category_url(self):
#     #     info = InfoTable.objects.get(pk=self.)
#     #     return reverse('category', info.category.cate)
#
#     def get_context_data(self, **kwargs):
#         context = super(InfoView, self).get_context_data(**kwargs)
#         return context

def info(request, pk):
    book_info = InfoTable.objects.get(pk=pk)

    return render(request, 'novel_site/info.html', context={
        'object': book_info,
    })


def detail(request, pk, index):
    book = InfoTable.objects.get(pk=1)
    chapter = book.all_chapters.get(pk=index)
    # chapter = BookTableOne.objects.get(pk=index)
    return render(request, 'novel_site/detail.html', context={
        'object': chapter,
    })


