# -*-coding:utf-8 -*-

"""
workflow:
1，生成一个有很多标题的txt
2，根据这个txt，去搜，并下载info资料，和小说下载的URL  get_novel_urls
3，把info塞到db里  insert_info
4，根据之前的url，去下载整本小说  download_novel
5，将小说分割成章节  product_split_rule --> bbb
6，把detail塞到db里  insert_detail

"""

import os
import codecs
import re
import pickle
import time
import random

import requests

from crawler.my_decorate import time_clock
from crawler.my_crawler import search_novel
from crawler.operateDB import get_infotable_count, get_title_id
from crawler.my_logger import MyLogger
from crawler.operateDB import insert_to_detail, insert_to_info, get_infotable_count


Logger = MyLogger('novel_operation')


@time_clock
def split_txt(txt_path, title, chapter_index, store_path, title_split=' ', title_rule=None):
    """
    将全本小说分割成独立章节，然后放到一个文件夹里
    t_rule = r'第一篇'  #  如果有多种方式，则传入list形式的rule
    t_path = 'test/xue.txt'
    title = book_name
    split_txt(t_path, title, t_rule, 1, store_path='./book/01')

    目前发现，正文部分前面都是有四个空格的，所以直接对首字判断即可
    """
    if not store_path.endswith('/'):  # 保证路径的存在
        store_path += '/'
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    try:
        chapter_index = int(chapter_index)
    except TypeError:
        print('index require num')
    chapter_index = chapter_index * 10000 + 1

    with codecs.open(txt_path, 'r', encoding='utf-8') as f:
        ls = f.readlines()
        start_index = None
        for index, line in enumerate(ls):
            flag = False
            if title_rule:  # 传入rule的话
                if isinstance(title_rule, list):
                    for tt in title_rule:
                        if re.match(tt, line):
                            flag = True
                            break
                else:
                    if re.match(title_rule, line):
                        flag = True
            else:
                if '\u4e00' <= line[0] <= '\u9fff' \
                        or '\u4e00' <= line[1] <= '\u9fff' and line[0] != '《':
                    # 1，中字开头的，2，标题是书名号开头的，所以没影响
                    flag = True

            if flag:
                if start_index is None:
                    start_index = index
                    tmp_ll = line.strip().split(title_split)
                    if not tmp_ll[-1]:
                        tmp_ll = tmp_ll[:-1]
                    if len(tmp_ll) == 2:
                        chapter_title = tmp_ll[-1]
                    elif len(tmp_ll) < 5:
                        chapter_title = ' '.join(tmp_ll[-2:])
                    # elif len(tmp_ll) == 5:
                    #     chapter_title = ' '.join(tmp_ll[-3:])
                    else:
                        chapter_title = ' '.join(tmp_ll[2:])
                    continue  # 跳过第一次

                end_index = index
                res = {
                    'id': chapter_index,
                    'title': title,
                    'chapter': chapter_title,
                    'content': ''.join(ls[start_index + 1:end_index-2]).replace('\r\n\r\n', '<br/>').replace('  ', '　'),
                }
                with open(store_path + str(chapter_index), 'wb') as wf:
                    pickle.dump(res, wf)
                chapter_index += 1
                start_index = end_index
                tmp_ll = line.strip().split(title_split)
                if not tmp_ll[-1]:
                    tmp_ll = tmp_ll[:-1]
                if len(tmp_ll) == 2:
                    chapter_title = tmp_ll[-1]
                elif len(tmp_ll) < 5:
                    chapter_title = ' '.join(tmp_ll[-2:])
                # elif len(tmp_ll) == 5:
                #     chapter_title = ' '.join(tmp_ll[-3:])
                else:
                    chapter_title = ' '.join(tmp_ll[2:])

        else:  # 最后一章
            res = {
                'id': chapter_index,
                'title': title,
                'chapter': chapter_title,
                'content': ''.join(ls[start_index + 1:end_index-2]).replace('\r\n\r\n', '<br/>').replace('  ', '　'),
            }
            with open(store_path + str(chapter_index), 'wb') as wf:
                pickle.dump(res, wf)


@time_clock
def get_novel_urls(file):
    """
    去那个网站搜这n本小说，如果有就下载相关info(生成pickle)，并将小说url放到download_url的txt中

    先去数据库中看info的index到多少了
    然后每个title需要与数据库对比是否存在
    :return:
    """

    SEARCH_URL = 'http://www.ranwenw.com/modules/article/search.php'

    book_index = get_infotable_count() + 1
    novel_download_url = []

    with codecs.open(file, 'r', encoding='utf-8') as rf:
        for title in rf.readlines():

            title = title.strip()

            # if get_title_id(title):
            #     Logger.warning('title is existed')
            #     continue

            url = search_novel(book_index, title, url=SEARCH_URL, store_path='./info/')
            if url:
                novel_download_url.append('{},{},{}'.format(str(book_index), title, url))
                book_index += 1
                Logger.debug('done {}'.format(title))
            else:
                Logger.debug('not found {}'.format(title))
            time.sleep(12)
        with codecs.open('novel_download_url.txt', 'w', encoding='utf-8') as wf:
            wf.write('\n'.join(novel_download_url))


@time_clock
def download_novel(file):
    """
    去文件中，下载url的的小说

    后面要用协程重写这一部分
    :return:
    """
    HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}
    with open(file, 'r') as rf:
        tt_list = rf.readlines()

    not_finish_list = []
    for line in tt_list:
        index, title, url = line.strip().split(',')
        try:
            res = requests.get(url, headers=HEADERS)
        except requests.exceptions.ConnectionError:
            Logger.warning('wrong in {}, {}'.format(index, title))
            not_finish_list.append(line)
            continue
        with codecs.open('./book/' + str(index) + '.txt', 'w', encoding='utf-8') as wf:
            wf.write(res.text)
        Logger.debug('done with {}, {}'.format(index, title))
        time.sleep(random.randint(0, 12))

    with open(file, 'w') as wf:
        wf.write('\n'.join(not_finish_list))


@time_clock
def product_txt_split_rule(start, end=None, file_path='./info/'):
    """
    去info这个文件夹下面，遍历pickle文件
    生成bbb函数的参数
    :param start:从第几本开始生产参数
    :param end:
    :param file_path:
    :return:
    """
    file_list = [file_path + str(i) for i in sorted(map(int, os.listdir(file_path)))]
    rule_list = []
    for i, file_name in enumerate(file_list[start:end], start=start):
        with open(file_name, 'rb') as rf:
            title = pickle.load(rf)['title']
        s = "./book/{i}.txt,{title},{i},./book/chapter/{i:0>2}, ".format(i=i, title=title)
        rule_list.append(s)
    with open('txt_split_rule.txt', 'w') as wf:
        wf.write('\n'.join(rule_list))
    return 'txt_split_rule.txt'


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
    if not store_path.endswith('/'):
        store_path += '/'
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


# @time_clock
# def get_url_from_redis(table_index):  # 这里的逻辑是一次只下载一本
#     if isinstance(table_index, list):
#         table_index = table_index[0]
#
#     conn = redis.StrictRedis()
#     length = conn.llen(table_index)
#     items = conn.lrange(table_index, 0, length-1)
#     detail_urls = []
#     for item in items:
#         index, url = str(item).split('!')
#         detail_urls.append([index[2:], url[:-1]])
#     download_detail(detail_urls)


@time_clock
def main(file):
    # get_novel_urls(file)
    # Logger.debug('already get novel download url')

    # info_index = get_infotable_count() + 1
    # insert_info(info_index)
    # Logger.debug('already insert info')

    # download_novel('novel_download_url.txt')
    # Logger.debug('already download the novel')
    info_index = 31
    product_txt_split_rule(info_index)

    # start_insert_detail(info_index)


if __name__ == '__main__':
    main('bbb.txt')

