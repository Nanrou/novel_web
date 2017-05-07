# -*- coding:utf-8 -*-

from django.shortcuts import render, loader, get_object_or_404, redirect
<<<<<<< HEAD
from django.urls import reverse
from django.http import HttpResponse
from .models import CategoryTable, InfoTable, BookTableOne
=======
>>>>>>> b1796c0599ff70904ff7f14c4e7005c09987b491
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView

# Create your views here.


def category(request, pk):
    pass


class InfoView(DetailView):

    model = InfoTable
    template_name = 'info.html'

    def get_context_data(self, **kwargs):
        context = super(InfoView, self).get_context_data(**kwargs)
        context['get_category_url'] = reverse('category', context['category'].cate)
        return context

# def info(request, pk):
#     book_info = InfoTable.objects.get(pk=pk)
#
#     return render(request, 'novel_site/info.html', context={
#         'objects': book_info,
#     })


def detail(request, pk):
<<<<<<< HEAD
    pass
    # try:
    #     table = NovelTable.objects.get(pk=pk)  # 在这里才实例化
    #     return render(request, 'novel_site/detail.html', context={'table': table})
    # except ObjectDoesNotExist:
    #     return index(request)
=======
>>>>>>> b1796c0599ff70904ff7f14c4e7005c09987b491
