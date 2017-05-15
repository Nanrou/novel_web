# -*- coding:utf-8 -*-

import os, sys

sys.path.append('../mysite/')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

try:
    from mysite.novel_site import models
except ImportError:
    from novel_site import models


def producte_cate():
    category = ['玄幻修仙', '科幻网游', '都市重生', '架空历史', '恐怖言情', '全本小说']
    cate = ['xuanhuan', 'kehuan', 'dushi', 'jiakong', 'kongbu', 'quanben']
    res = []
    for i in range(len(cate)):
        res.append({'id': i+1, 'category': category[i], 'cate': cate[i]})
    return res


if __name__ == '__main__':
    pass
    # p_list = producte_cate()
    # instance_list = []
    # for item in p_list:
    #     instance_list.append(models.CategoryTable(id=item['id'], category=item['category'], cate=item['cate']))
    #
    # # models.CategoryTable.objects.bulk_create(instance_list)
    # for index, i in enumerate(instance_list):
    #     if index < 2:
    #         continue
    #     i.save()


