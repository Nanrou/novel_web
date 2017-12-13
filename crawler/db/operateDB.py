# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime, timedelta
import pickle
import re
from collections.abc import MutableSequence

from utls.my_logger import MyLogger

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_DIR, 'novel'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel.novel.settings.dev')

import django

django.setup()

from pc import models

from django.db.models import ObjectDoesNotExist

"""
约定
info的pickle文件的dict结构应为
{
    'name': ,
    'author': ,
    'category': ,
    'resume': ,
    'update_time': ,

}

detail的pickle文件的dict结构应为
{
    'title': ,
    'chapter': ,
    'content': ,
}
"""

Logger = MyLogger('DB_log')

MODIFIED_TEXT = [r'一秒记住.*?。', r'(看书.*?)', r'纯文字.*?问', r'热门.*?>', r'最新章节.*?新',
                 r'は防§.*?e',
                 r'复制.*?>', r'字-符.*?>', r'最新最快，无.*?。',
                 r'&.*?;', r'(2|w|ｗ).*(g|m|ｍ) ',
                 ]

CATEGORY_DICT = {
    '言情': '都市',
    '军事': '架空',
    '仙侠': '玄幻',
}


def insert_to_category():  # 将分类插入数据库，加了一个防止重复插入的判断
    if models.CategoryTable.objects.all().exists():
        Logger.warning('category table is none null, maybe already inserted')
        return

    def product_cate():  # 这是初始化的时候做的
        category = ['经典悬疑', '玄幻修真', '科幻网游', '都市重生', '架空历史', '武侠世界', '全本小说']
        cate = ['xuanyi', 'xuanhuan', 'kehuan', 'dushi', 'jiakong', 'wuxia', 'quanben']
        _res = []
        for i in range(len(cate)):
            _res.append({'id': i + 1, 'category': category[i], 'cate': cate[i]})
        return _res

    res = product_cate()
    for r in res:
        models.CategoryTable.objects.create(**r)


def insert_to_book(files):  # 将书的信息插入数据库，可以传入单个文件或者多个文件
    """
    col: id | title | status | update_time | image | resume | author_id | category_id

    这里只处理pickle文件

    :param files: 包含文件名的列表
    :return:
    """
    if isinstance(files, MutableSequence):  # 判断传入是单个还是多个
        info_list = []
        for file in files:  # 如果传入的是文件名的列表，就用一次插入多条
            with open(file, 'rb') as rf:
                res = operate_info_res(pickle.load(rf))  # 读取pickle文件，并逐项操作
                info_list.append(models.BookTable(**res))  # 生成那一行的实例
            Logger.debug('insert {}'.format(file))
        models.BookTable.objects.bulk_create(info_list)  # 一次插入
    else:
        with open(files, 'rb') as rf:
            res = operate_info_res(pickle.load(rf))
            models.BookTable.objects.update_or_create(**res)
            Logger.debug('insert {}'.format(files))


def operate_info_res(res):  # 修正res中的内容
    """

    :param res:
    :return:
    """
    res['title'] = res['name']
    res.pop('name')

    author = res['author']
    res['author_id'] = get_author_id(author)  # 拿到作者表中的id
    res.pop('author')

    category = res['category']
    res['category_id'] = get_category_id(category)  # 拿到分类中的id
    res.pop('category')

    # 根据更新时间判定是否完结
    update_time = datetime.strptime(res['update_time'], '%Y-%m-%d %H:%M')
    if datetime.now() - update_time > timedelta(30):
        res['_status'] = 1
    else:
        res['_status'] = 0

    if len(res['resume']) > 280:
        if '<br/>' in res['resume']:
            while '<br/>' in res['resume'] and len(res['resume']) > 280:
                res['resume'] = res['resume'].rsplit('<br/>', 1)[0]
        else:
            res['resume'] = res['resume'][:290]

    return res


def insert_to_detail(files, **kwargs):  # 插入章节
    if isinstance(files, list):
        part_list = []
        if len(files) > 50:  # 以50次为单位插入
            part_list = [files[i:i + 50] for i in range(0, len(files), 50)]
        else:
            part_list.append(files)
        for file_list in part_list:
            detail_list = []
            for file in file_list:
                with open(file, 'rb') as rf:
                    try:
                        res = operate_detail_res(pickle.load(rf))
                    except RuntimeError:
                        Logger.warning('{}:wrong in {}'.format(datetime.now(), file))
                    res['id'] = file.split('/')[-1]  # 就拿章节文件名来做pk
                    res.update(kwargs)
                    detail_list.append(models.BookTableOne(**res))  # 创建实例，放到list里
            models.BookTableOne.objects.bulk_create(detail_list)  # 一次插入list里的所有实例
            Logger.info('insert {} - {}'.format(file_list[0], file_list[-1]))
    else:
        with open(files, 'rb') as rf:
            res = operate_detail_res(pickle.load(rf))
            res['id'] = files.split('/')[-1]
            res.update(kwargs)
            models.BookTableOne.objects.create(**res)
        Logger.info('insert {}'.format(files))


def new_insert_chapters(chapters):
    all_chapter = []
    for index, chapter in enumerate(chapters):
        res = operate_detail_res(chapter)
        all_chapter.append(models.ChapterTable(**res))
        if index % 100 == 0:
            models.ChapterTable.objects.bulk_create(all_chapter)
            Logger.info('done {}'.format(index))
            all_chapter = []
    models.ChapterTable.objects.bulk_create(all_chapter)
    Logger.info('success insert {} chapter'.format(index))


def operate_detail_res(res):  # 处理细节
    """
    col: id | chapter | content | need_confirm | book_id | title_id

    attr_list = ['title', 'chapter', 'content']
    """

    res['content'], res['need_confirm'] = filter_content(res['content'])

    res.update(get_title_id(res['title']))
    res.pop('title')
    return res


def get_author_id(name):  # 拿到author的id
    name = name if '：' not in name else name.split('：')[-1]
    name = name if '(' not in name else name.split('(')[0]
    obj, created = models.AuthorTable.objects.get_or_create(author=name)
    return obj.id


def get_category_id(category):  # 拿到分类的id
    if category in CATEGORY_DICT:
        category = CATEGORY_DICT[category]
    for cate in category:
        obj = models.CategoryTable.objects.get(category__contains=cate)
        if obj:
            return obj.id
    Logger.warning('miss category')
    return 'miss'


def get_title_id(title):  # 拿到title的id
    try:
        obj = models.BookTable.objects.only('id').get(title=title)
    except ObjectDoesNotExist:
        Logger.warning("InfoTable hasn't {}".format(title))
        return None
    return {'title_id': obj.id, 'book_id': obj.id, 'book_name': title}


def filter_content(txt):
    """
    过滤文件中想要过滤的东西
    :param txt:
    :return:
    """
    need_confirm = 0
    # if 'div' in txt:  # 去头尾标签
    #     txt = txt.split('<div id="content">')[-1].split('</div>')[0]
    # if len(txt.strip()) > 0:  # 去头乱码
    #     while True:
    #         if txt.startswith(' ') or txt.startswith('　'):
    #             break
    #         try:
    #             if '\u4e00' <= txt[0] <= '\u9fff':
    #                 break
    #         except IndexError:
    #             raise RuntimeError(' i m here')
    #         txt = txt[1:]

    for ccc in MODIFIED_TEXT:  # 正则去广告
        txt = re.sub(ccc, '', txt)
    if '\\' in txt or len(txt) < 100:
        need_confirm = 1
    return txt, need_confirm


def update_img_path(start=None, end=None):
    """
    批量插入图片路径，若图片不存在则为miss
    :param start:因为现在书的序号是从1开始的，所以start值需要减1
    :param end:
    :return:
    """
    t_list = models.InfoTable.objects.all()[start - 1: end].only('id', 'image')
    for ins in t_list:
        index = str(ins.id)
        if os.path.exists('../mysite/novel_site/static/novel_site/images/{}s.jpg'.format(index)):
            ins.image = 'novel_site/images/{}s.jpg'.format(index)
        else:
            ins.image = 'novel_site/images/miss.jpg'
        ins.save()


def update_update_time(start=1, end=None):
    """
    批量参入更新时间
    :param start:因为现在书的序号是从1开始的，所以start值需要减1
    :param end:
    :return:
    """
    t_list = models.InfoTable.objects.all()[start - 1: end].only('update_time')
    for ins in t_list:
        ins.update_time = datetime.datetime.now().isoformat(' ', timespec='seconds')
        ins.save()


def get_infotable_count():
    return models.InfoTable.objects.count()


def del_book_chapters(num, table=models.ChapterTable):
    """
    删除指定书的章节
    :param num: 书的序号
    :param table:
    :return:
    """
    assert isinstance(num, int)
    _floor = num * 10000
    _limit = (num + 1) * 10000
    table.objects.filter(id__gt=_floor, id__lt=_limit).delete()


def add_latest_chapters_and_them_url(num):
    books_num = get_infotable_count()
    for pk in range(num, books_num + 1):
        try:
            book = models.BookTableOne.objects.filter(title_id=pk).only('id', 'title').order_by('-id')[0]
            info = models.InfoTable.objects.only('latest_chapter', 'latest_chapter_url').get(id=pk)

            info.latest_chapter = book.chapter
            info.latest_chapter_url = '/book/{}/{}/'.format(pk, book.id)
            info.save()

        except IndexError:
            pass


def update_page_relation(pk):  # 更新所有章节的前后跳转
    book = models.BookTable.objects.get(id=pk)
    tmp = None
    for chapter in book.all_chapters.defer('content', 'chapter').all().order_by('id'):
        if tmp is None:
            tmp = chapter
            continue
        tmp.next_chapter_id = chapter.id
        chapter.prev_chapter_id = tmp.id
        tmp.save()
        chapter.save()
        tmp = chapter


if __name__ == '__main__':
    print('i am in ORM')
    # update_page_relation(1)
    # insert_to_category()
    # update_update_time()
    # del_book_chapters(30)
    # add_latest_chapters_and_them_url(3)
