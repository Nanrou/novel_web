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

import pickle
import re

MODIFIED_TEXT = [r'一秒记住.*?。', r'(看书.*?)', r'纯文字.*?问', r'热门.*?>', r'最新章节.*?新',
                 r'は防§.*?e',
                 # r'&.*?>', r'c.*?>',
                 r'复制.*?>', r'字-符.*?>', r'最新最快，无.*?。',
                 r'    .Shumilou.Co  M.Shumilou.Co<br /><br />', r'[Ww]{3}.*[mM]',
                 r'&amp;nbsp;    &amp;nbsp;    &amp;nbsp;    &amp;nbsp;  ']


def producte_cate():
    category = ['玄幻修仙', '科幻网游', '都市重生', '架空历史', '恐怖言情', '全本小说']
    cate = ['xuanhuan', 'kehuan', 'dushi', 'jiakong', 'kongbu', 'quanben']
    res = []
    for i in range(len(cate)):
        res.append({'id': i+1, 'category': category[i], 'cate': cate[i]})
    return res


def insert_to_info(file, store_des=1, pk=None):
    with open(file, 'rb') as rf:
        res = pickle.load(rf)

        if pk:
            res['id'] = pk

        res['status'] = res['status'][0].split('：')[-1][:3]
        res['store_des'] = store_des

        name = res['author']
        res['author_id'] = get_author_id(name)
        res.pop('author')

        category = res['category']
        res['category_id'] = get_category_id(category)
        res.pop('category')

        models.InfoTable.objects.create(**res)


def insert_to_detail(file, **kwargs):  # 准备改成bulk create
    with open(file, 'rb') as rf:
        res = pickle.load(rf)

        while True:
            if '\u4e00' <= res['chapter'] <= '\u9fff':
                break
            res['chapter'] = res['chapter'][1:]

        res['content'], res['need_confirm'] = filter_content(res['content'])

        res.update(get_title_id(res['title']))
        res.pop('title')

        res.update(kwargs)
        models.BookTableOne.objects.create(**res)


def get_author_id(name):
    name = name.split('：')[-1]
    obj, created = models.AuthorTable.objects.get_or_create(author=name)
    return obj.id


def get_category_id(category):
    category = category[:2]
    obj = models.CategoryTable.objects.get(category__contains = category)
    return obj.id


def get_title_id(title):
    obj = models.InfoTable.objects.only('id').get(title=title)
    return {'title_id': obj.id, 'book_id': obj.id}


def filter_content(txt):
    need_confirm = 0
    if 'div' in txt:  # 去头尾标签
        txt = txt.split('<div id="content">')[-1].split('</div>')[0]
    if len(txt) > 0:  # 去头乱码
        while True:
            if txt.startswith(' ') or txt.startswith('　'):
                break
            if '\u4e00' <= txt[0] <= '\u9fff':
                break
            txt = txt[1:]
    for ccc in MODIFIED_TEXT:  # 正则去广告
        txt = re.sub(ccc, '', txt)
    if '\\' in txt or len(txt) < 100:
        need_confirm = 1
    return txt, need_confirm


if __name__ == '__main__':

    # file_name = './bbb/0'
    # insert_to_info(file_name)

    file_name = './ccc/0'
    insert_to_detail(file_name)
