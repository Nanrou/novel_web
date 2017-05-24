# -*- coding:utf-8 -*-

import os, sys
import datetime

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
from my_crawler import image_download
from my_logger import MyLogger

Logger = MyLogger('DB_log')

MODIFIED_TEXT = [r'一秒记住.*?。', r'(看书.*?)', r'纯文字.*?问', r'热门.*?>', r'最新章节.*?新',
                 r'は防§.*?e',
                 # r'&.*?>', r'c.*?>',
                 r'复制.*?>', r'字-符.*?>', r'最新最快，无.*?。',
                 r'    .Shumilou.Co  M.Shumilou.Co<br /><br />', r'[Ww]{3}.*[mM]',
                 r'&amp;nbsp;    &amp;nbsp;    &amp;nbsp;    &amp;nbsp;  ',
                 r'.*\u3000\u3000第.*?章.*?<br/>',
                 ]


def product_cate():
    category = ['玄幻修真', '科幻网游', '都市重生', '架空历史', '恐怖灵异', '全本小说']
    cate = ['xuanhuan', 'kehuan', 'dushi', 'jiakong', 'kongbu', 'quanben']
    res = []
    for i in range(len(cate)):
        res.append({'id': i+1, 'category': category[i], 'cate': cate[i]})
    return res


def insert_to_category():
    res = product_cate()
    for r in res:
        models.CategoryTable.objects.create(**r)


def insert_to_info(files, store_des=1, pk=None):
    """
    col: id | title | status | update_time | store_des | image | resume | author_id | category_id


    :param files:
    :param store_des:
    :param pk:
    :return:
    """
    if isinstance(files, list):  # 判断传入是单个还是多个
        info_list = []
        for file in files:
            with open(file, 'rb') as rf:
                res = operate_info_res(pickle.load(rf), store_des, pk)
                info_list.append(models.InfoTable(**res))
            Logger.debug('insert {}'.format(file))
        models.InfoTable.objects.bulk_create(info_list)
    else:
        with open(files, 'rb') as rf:
            res = operate_info_res(pickle.load(rf), store_des, pk)
            models.InfoTable.objects.create(**res)
            Logger.debug('insert {}'.format(files))


def operate_info_res(res, store_des, pk):  # 修正res中的内容
    if pk:
        res['id'] = pk

    if '：' in res['status'] or '：' in res['status']:
        res['status'] = res['status'][0].split('：')[-1][:3]

    res['store_des'] = store_des

    name = res['author']
    res['author_id'] = get_author_id(name)
    res.pop('author')

    category = res['category']
    res['category_id'] = get_category_id(category)
    res.pop('category')

    img_url = res['img_url']
    img_path = 'miss'
    if img_url:
        index = res.get('id', 'tmp')
        img_path = image_download(index, img_url)
    res['image'] = img_path
    res.pop('img_url')

    return res


def insert_to_detail(files, **kwargs):
    if isinstance(files, list):
        part_list = []
        if len(files) > 50:  # 以50次为单位插入
            part_list = [files[i:i+50] for i in range(0, len(files), 50)]
        else:
            part_list.append(files)
        for file_list in part_list:
            detail_list = []
            for file in file_list:
                with open(file, 'rb') as rf:
                    try:
                        res = operate_detail_res(pickle.load(rf))
                    except RuntimeError:
                        with open('miss_chapter.txt', 'a') as wf:
                            wf.write('{}:wrong in {}'.format(datetime.datetime.now(), file))  # res会使用上次的
                    res['id'] = file.split('/')[-1]
                    res.update(kwargs)
                    detail_list.append(models.BookTableOne(**res))  # 创建实例，放到list里
            models.BookTableOne.objects.bulk_create(detail_list)  # 一次插入list里的所有实例
            Logger.debug('insert {} - {}'.format(file_list[0], file_list[-1]))
    else:
        with open(files, 'rb') as rf:
            res = operate_detail_res(pickle.load(rf))
            res['id'] = files.split('/')[-1]
            res.update(kwargs)
            models.BookTableOne.objects.create(**res)
        Logger.debug('insert {}'.format(files))


def operate_detail_res(res):
    """
    col: id | chapter | content | need_confirm | book_id | title_id

    """

    attr_list = ['id', 'chapter', 'content']

    # while True:
    #     if '\u4e00' <= res['chapter'][0] <= '\u9fff':  # 只是过滤章节名前的空格
    #         break
    #     res['chapter'] = res['chapter'][1:]
    res['chapter'] = res['chapter'].strip()
    res['content'], res['need_confirm'] = filter_content(res['content'])

    res.update(get_title_id(res['title']))
    res.pop('title')
    return res


def get_author_id(name):
    name = name.split('：')[-1]
    obj, created = models.AuthorTable.objects.get_or_create(author=name)
    return obj.id


def get_category_id(category):
    category = category[:2]
    obj = models.CategoryTable.objects.get(category__contains=category)
    return obj.id


def get_title_id(title):
    obj = models.InfoTable.objects.only('id').get(title=title)
    return {'title_id': obj.id, 'book_id': obj.id}


def filter_content(txt):
    need_confirm = 0
    if 'div' in txt:  # 去头尾标签
        txt = txt.split('<div id="content">')[-1].split('</div>')[0]
    if len(txt.strip()) > 0:  # 去头乱码
        while True:
            if txt.startswith(' ') or txt.startswith('　'):
                break
            try:
                if '\u4e00' <= txt[0] <= '\u9fff':
                    break
            except IndexError:
                raise RuntimeError(' i m here')
            txt = txt[1:]
        for ccc in MODIFIED_TEXT:  # 正则去广告
            txt = re.sub(ccc, '', txt)
    if '\\' in txt or len(txt) < 100:
        need_confirm = 1
    return txt, need_confirm


def update_img_path(start=None, end=None):
    """
    批量插入图片路径，若图片不存在则为miss
    :param start:
    :param end:
    :return:
    """
    t_list = models.InfoTable.objects.all()[start: end].only('id', 'image')
    for ins in t_list:
        index = str(ins.id)
        if os.path.exists('../mysite/novel_site/static/novel_site/images/{}s.jpg'.format(index)):
            ins.image = 'novel_site/images/{}s.jpg'.format(index)
        else:
            ins.image = 'novel_site/images/miss.jpg'
        ins.save()


def update_update_time(start=None, end=None):
    """
    批量参入更新时间
    :param start:
    :param end:
    :return:
    """
    t_list = models.InfoTable.objects.all()[start: end].only('update_time')
    for ins in t_list:
        ins.update_time = datetime.datetime.now().isoformat(' ', 'seconds')
        ins.save()


if __name__ == '__main__':

    # file_name = './bbb/0'
    # insert_to_info(file_name)

    # file_name = './ccc/0'
    # insert_to_detail(file_name)

    # insert_to_category()
    print('i am in ORM')
    # update_img_path()
    # update_update_time()