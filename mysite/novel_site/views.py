# -*- coding:utf-8 -*-

from django.shortcuts import render, loader, get_object_or_404, redirect
from django.http import HttpResponse
from .models import NovelTable
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def index(request):
    chapter_list = NovelTable.objects.order_by('id')[:5]

    return render(request, 'novel_site/index.html', context={
        'chapter_list': chapter_list,
    })

    # template = loader.get_template('novel_site/index.html')
    # context = {
    #     'title': 'home', 'welcome': 'hello world',
    # }
    # return HttpResponse(template.render(context, request))


def detail(request, pk):
    try:
        table = NovelTable.objects.get(pk=pk)  # 在这里才实例化
        return render(request, 'novel_site/detail.html', context={'table': table})
    except ObjectDoesNotExist:
        return index(request)
