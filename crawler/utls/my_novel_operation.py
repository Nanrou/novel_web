# -*-coding:utf-8 -*-

"""

"""

import os
import codecs
import re
import pickle
import time
import random

import requests

from crawler.utls.my_decorate import time_clock
from crawler.db.operateDB import get_infotable_count, get_title_id
from crawler.utls.my_logger import MyLogger
from crawler.db.operateDB import insert_to_detail, insert_to_info, get_infotable_count


Logger = MyLogger('novel_operation')

MODIFIED_TEXT = [r'一秒记住.*?。', r'(看书.*?)', r'纯文字.*?问', r'热门.*?>', r'最新章节.*?新',
                 r'は防§.*?e',
                 r'复制.*?>', r'字-符.*?>', r'最新最快，无.*?。',
                 r'&.*?;', r'(2|w|ｗ).*(g|m|t|ｍ|ｔ)', r'\u3000\u3000\n\n',
                 r'。.*小说',
                 ]


@time_clock
def split_book(txt_path, title, chapter_index, store_path, chapter_split=' ', chapter_rule=None):
    """
    将全本小说分割成独立章节，然后放到一个文件夹里
    t_rule = r'第一篇'  如果有多种方式，则传入list形式的rule
    t_path = 'test/xue.txt'
    title = book_name  书名
    split_txt(t_path, title, t_rule, 1, store_path='./book/01')

    目前发现，正文部分前面都是有四个空格的，所以直接对首字判断即可
    书的格式一般为
        《书名》

        第一章 章节名
            正文
            。。。
        第二章 章节名
            正文
            。。。

    :param txt_path: 书的位置
    :param title: 书名
    :param chapter_index: 序号，也就是书的pk
    :param store_path: 分割完后的存放位置
    :param chapter_split: 章节名那一行的分隔符
    :param chapter_rule: 特殊的分割条件，因为一般情况下，章节那一行是没有空格的，而正文都是有空格在前面的
    :return:
    """
    with open(txt_path, 'r', encoding='utf-8') as rf:
        txt = rf.read()

    with open('tmp', 'w', encoding='utf-8') as wf:
        wf.write(filter_content(txt))

    # if not store_path.endswith('/'):  # 保证路径的存在
    #     store_path += '/'
    if not os.path.exists(store_path):
        os.mkdir(store_path)

    try:
        chapter_index = int(chapter_index) * 10000 + 1
    except TypeError:
        raise TypeError

    with codecs.open('tmp', 'r', encoding='utf-8') as f:
        book = f.readlines()
        start_index = None
        chapter_title = ''
        for index, line in enumerate(book):
            if chapter_rule:  # 传入rule的话
                raise RuntimeError('wait to finish')
                # if isinstance(chapter_rule, list):
                #     for tt in chapter_rule:
                #         if re.match(tt, line):
                #             flag = True  # 看一下这个flag怎么处理比较好
                #             break
                # else:
                #     assert isinstance(chapter_rule, str) is True, 'title rule must be str, if it is not a list'
                #     if re.match(chapter_rule, line):
                #         flag = True
            else:
                if '\u4e00' <= line[0] <= '\u9fff' and chapter_split in line \
                    or '\u4e00' <= line[0] <= '\u9fff' and len(line) < 10 \
                        or ('\u4e00' <= line[1] <= '\u9fff' and line[0] != '《'):
                    # 1，中文编码开头的，2，由于书名是书名号开头的，所以只要不是书名号开头的，就是章节行
                    # 从这一行开始标记
                    if start_index is None:
                        start_index = index
                        tmp_ll = line.strip().split(chapter_split)
                        if len(tmp_ll) == 2:
                            chapter_title = tmp_ll[-1]
                        elif len(tmp_ll) < 5:
                            chapter_title = ' '.join(tmp_ll[-2:])
                        else:
                            chapter_title = ' '.join(tmp_ll[2:])
                        continue  # 跳过第一次

                    end_index = index
                    res = {
                        'id': chapter_index,
                        'title': title,
                        'chapter': chapter_title,
                        'content': ''.join(book[start_index + 1: end_index]).replace('\r\n\r\n', '<br/>').replace('  ', '　'),
                    }
                    with open(os.path.join(store_path, str(chapter_index)), 'wb') as wf:
                        pickle.dump(res, wf)
                    chapter_index += 1

                    start_index = end_index  # 将当前行标记为新的开始
                    tmp_ll = line.strip().split(chapter_split)
                    if len(tmp_ll) == 2:
                        chapter_title = tmp_ll[-1]
                    elif len(tmp_ll) < 5:
                        chapter_title = ' '.join(tmp_ll[-2:])
                    else:
                        chapter_title = ' '.join(tmp_ll[2:])

        else:  # 最后一章
            print(start_index)
            res = {
                'id': chapter_index,
                'title': title,
                'chapter': chapter_title,
                'content': ''.join(book[start_index + 1:]).replace('\r\n\r\n', '<br/>').replace('  ', '　'),
            }
            with open(os.path.join(store_path, str(chapter_index)), 'wb') as wf:
                pickle.dump(res, wf)


def filter_content(txt):
    """
    过滤文本
    :param txt:
    :return:
    """
    # if 'div' in txt:  # 去头尾标签
    #     txt = txt.split('<div id="content">')[-1].split('</div>')[0]
    for rule in MODIFIED_TEXT:  # 正则去广告
        txt = re.sub(rule, '', txt, flags=re.I)
    txt = re.sub(r'\n\n\n+', '\n\n', txt)
    return txt


@time_clock
def bbb(file):
    """
    根据file中的参数，去运行小说分割
    后面可以尝试多进程
    :param file:
    :return:
    """
    with open(file, 'r') as rf:
        res_list = rf.readlines()
    for index, line in enumerate(res_list):
        var_list = line.strip('\n').split(',')
        Logger.debug('start split {}'.format(var_list))
        try:
            split_txt(*var_list)
            Logger.debug('Finish split {}'.format(var_list))
        except IndexError or UnicodeError as e:  # 在出错的情况下，不用手动删除已完成的
            Logger.warning('{} happen in {}'.format(e, var_list))
            with open(file, 'w') as wf:
                wf.write('\n'.join(res_list[index:]))


@time_clock
def insert_info(start, store_path='./info/'):  # 要指明从第几本开始输入
    info_list = (store_path + str(i) for i in sorted(map(int, os.listdir(store_path)))[start-1:])
    for index, info in enumerate(info_list, start=start):  # 这里的逻辑是一次插入一个info
        insert_to_info(info, pk=int(index))


@time_clock
def insert_detail(store_path):  # 这里逻辑改一下，每次只导入一本书
    detail_list = [store_path + str(i) for i in sorted(map(int, os.listdir(store_path)))]
    insert_to_detail(detail_list)


@time_clock
def start_insert_detail(start, path='./book/chapter/'):
    """

    :param start: 从第start本开始塞进去
    :param path:
    :return:
    """
    book_paths = [path + str(i) for i in sorted(map(int, os.listdir('./book/chapter/')))[start-1:]]
    for book_path in book_paths:
        insert_detail(book_path)



@time_clock
def main(file):
    # get_novel_urls(file)
    # Logger.debug('already get novel download url')
    #
    # info_index = get_infotable_count() + 1
    # insert_info(info_index)
    # Logger.debug('already insert info')
    info_index = 30
    download_novel('novel_download_url.txt')
    Logger.debug('already download the novel')
    bbb(product_txt_split_rule(info_index))

    start_insert_detail(info_index)


if __name__ == '__main__':
    # main('bbb.txt')
    # split_book('160163.txt', '惊悚乐园', 30, './test/')
    # insert_detail('./test/')
    print('')
