# -*- coding:utf-8 -*-

import os
import sys
import datetime
import pickle
import re

from crawler.utls.my_logger import MyLogger

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_DIR, 'mysite/'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

import django
django.setup()

try:
    from mysite.novel_site import models
except ImportError:
    from novel_site import models

from django.db.models import ObjectDoesNotExist


"""
约定
info的pickle文件的dict结构应为
{
    'title': ,
    'author': ,
    'category': ,
    'resume': ,

}

detail的pickle文件的dict结构应为
{
    'id': ,
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
    '武侠': '架空',
    '仙侠': '玄幻',
}


def product_cate():  # 这是初始化的时候做的
    category = ['玄幻修真', '科幻网游', '都市重生', '架空历史', '恐怖灵异', '全本小说']
    cate = ['xuanhuan', 'kehuan', 'dushi', 'jiakong', 'kongbu', 'quanben']
    res = []
    for i in range(len(cate)):
        res.append({'id': i+1, 'category': category[i], 'cate': cate[i]})
    return res


def insert_to_category():  # 将分类插入数据库，加了一个防止重复插入的判断
    if models.CategoryTable.objects.all().exsits():
        Logger.warning('category table is none null, maybe already inserted')
        return
    res = product_cate()
    for r in res:
        models.CategoryTable.objects.create(**r)


def insert_to_info(files, store_des=1):  # 将info信息插入db
    """
    col: id | title | status | update_time | store_des | image | resume | author_id | category_id

    这里只处理pickle文件，而pickle文件又是以pk命名的，所以直接拿文件名做pk就可以了

    :param files: 包含文件名的列表
    :param store_des: 存到哪个数据库
    :return:
    """
    if isinstance(files, list):  # 判断传入是单个还是多个
        info_list = []
        for file in files:  # 如果传入的是文件名的列表，就用一次插入多条
            with open(file, 'rb') as rf:
                res = operate_info_res(pickle.load(rf), store_des, pk=file.split('/')[-1])  # 读取pickle文件，并逐项操作
                info_list.append(models.InfoTable(**res))  # 生成那一行的实例
            Logger.debug('insert {}'.format(file))
        models.InfoTable.objects.bulk_create(info_list)  # 一次插入
    else:
        with open(files, 'rb') as rf:
            res = operate_info_res(pickle.load(rf), store_des, pk=files.split('/')[-1])
            models.InfoTable.objects.update_or_create(**res)
            Logger.debug('insert {}'.format(files))


def operate_info_res(res, store_des, pk):  # 修正res中的内容
    """

    :param res:
    :param store_des: 是指小说在第几个数据库
    :param pk:
    :return:
    """
    if pk:  # 传入pk的话就指定，否则让orm自己指定
        res['id'] = pk

    if 'status' in res:  # 连载或者完结的值，只是换了个键名
        if ('：' or ':') in res['status']:
            res['status'] = res['status'][0].split('：')[-1][:3]
        res['_status'] = res['status']
        res.pop('status')

    # 去掉摘要中的空格
    if '\xa0' in res['resume']:
        res['resume'] = res['resume'].replace('\xa0', '')
    if '\u3000' in res['resume']:
        res['resume'] = res['resume'].replace('\u3000', '')

    res['store_des'] = store_des

    name = res['author']
    res['author_id'] = get_author_id(name)  # 拿到作者表中的id
    res.pop('author')

    category = res['category']
    res['category_id'] = get_category_id(category)  # 拿到分类中的id
    res.pop('category')

    # 输入image的路径
    if pk:
        res['image'] = pk + '.jpg'
    else:
        res['image'] = res['title'] + '.jpg'

    # 把状态转换成0和1
    if res['_status'] == '连载中':
        res['_status'] = 0
    else:
        res['_status'] = 1

    # 输入更新时间
    res['update_time'] = datetime.datetime.now().isoformat(' ', timespec='seconds')

    return res


def insert_to_detail(files, **kwargs):  # 插入章节
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
                        Logger.warning('{}:wrong in {}'.format(datetime.datetime.now(), file))
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


def operate_detail_res(res):  # 处理细节
    """
    col: id | chapter | content | need_confirm | book_id | title_id

    attr_list = ['id', 'chapter', 'content']
    """

    res['chapter'] = res['chapter'].strip()
    res['content'], res['need_confirm'] = filter_content(res['content'])

    res.update(get_title_id(res['title']))
    res.pop('title')
    return res


def get_author_id(name):  # 拿到author的id
    name = name if '：' not in name else name.split('：')[-1]
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
        obj = models.InfoTable.objects.only('id').get(title=title)
    except ObjectDoesNotExist:
        print("InfoTable hasn't {}".format(title))
        return None
    return {'title_id': obj.id, 'book_id': obj.id}


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
    #     for ccc in MODIFIED_TEXT:  # 正则去广告
    #         txt = re.sub(ccc, '', txt)
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
    t_list = models.InfoTable.objects.all()[start-1: end].only('id', 'image')
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
    t_list = models.InfoTable.objects.all()[start-1: end].only('update_time')
    for ins in t_list:
        ins.update_time = datetime.datetime.now().isoformat(' ', timespec='seconds')
        ins.save()


def get_infotable_count():
    return models.InfoTable.objects.count()


def del_book_chapters(num, table=models.BookTableOne):
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

if __name__ == '__main__':

    print('i am in ORM')
    # update_update_time()
    del_book_chapters(30)
