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
#     # def get(self, request, *args, **kwargs):
#
#     # def get_category_url(self):
#     #     info = InfoTable.objects.get(pk=self.)
#     #     return reverse('category', info.category.cate)
#
#     def get_context_data(self, **kwargs):
#         context = super(InfoView, self).get_context_data(**kwargs)
#         context['get_category_url'] = 1111
#         return context

def info(request, pk):
    while True:
        if not pk.startswith('0'):
            break
        pk = pk[1:]
    book_info = InfoTable.objects.get(pk=pk)

    return render(request, 'novel_site/info.html', context={
        'objects': book_info,
    })


def detail(request, pk):
    while True:
        if not pk.startswith('0'):
            break
        pk = pk[1:]


