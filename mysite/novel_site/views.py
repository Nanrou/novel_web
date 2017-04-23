# -*- coding:utf-8 -*-

from django.shortcuts import render, loader, get_object_or_404, _get_queryset
from django.http import HttpResponse
from .models import NovelTable

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
    table = get_object_or_404(NovelTable, pk=pk)
    return render(request, 'novel_site/detail.html', context={'table': table})