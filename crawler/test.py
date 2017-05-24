# -*- coding:utf-8 -*-


import aiohttp
import asyncio
import pickle
import random
import re
from contextlib import contextmanager

from lxml import etree
import codecs
import time
import requests
import os
from crawler.my_decorate import time_clock


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}
URL = 'http://www.ranwen.org/files/article/56/56048/10973525.html'
# URL = 'http://www.ranwen.org/files/article/56/56048/'

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            page = await resp.text()
            page = etree.HTML(page)
            content = page.xpath('//div[@class="bookname"]/h1')
            # content = page.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href')
            print(type(content))
            print(len(content))
            for c in content:
                # print(etree.tounicode(c))
                print(c)


@time_clock
def split_txt(txt_path, title, chapter_index, store_path='./', title_split=' ', title_rule=None):
    """
    将全本小说分割成独立章节，然后放到一个文件夹里
    t_rule = r'第一篇'  #  如果有多种方式，则传入list形式的rule
    t_path = 'test/xue.txt'
    title = book_name
    split_txt(t_path, title, t_rule, 1, store_path='./book/01')

    目前发现，正文部分前面都是有四个空格的，所以对首字判断
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
                if '\u4e00' <= line[0] <= '\u9fff':  # 只要是中字开头的，标题是书名号开头的，所以没影响
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
                        # 'content': ''.join(ls[start_index + 1:end_index-2]),
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
                # 'content': ''.join(ls[start_index + 1:end_index-2]),
            }
            with open(store_path + str(chapter_index), 'wb') as wf:
                pickle.dump(res, wf)


def get_urls():
    """
    去那个网站搜这50个名字的小说，如果有就下载相关info
    :return:
    """
    from my_crawler import search_novel

    SEARCH_URL = 'http://www.ranwenw.com/modules/article/search.php'
    download_url = {}
    with codecs.open('titles_list.txt', 'r', encoding='utf-8') as rf:
        for index, title in enumerate(rf.readlines(), start=1):

            title = title.strip()
            url = search_novel(index, title, url=SEARCH_URL, stone_path='./info/')
            if url:
                print('done {}'.format(title))
            else:
                url = ''
                print('not found {}'.format(title))
            time.sleep(12)

            with codecs.open('download_url', 'a', encoding='utf-8') as wf:
                wf.write(title + ',' + url + '\n')


def get_img(index, title):
    """
    去另外一个网站下载那些小说的封面图片
    :param index:
    :param title:
    :return:
    """
    HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}
    # res = requests.post(url, data=var, headers=HEADERS)
    res = requests.get('http://so.ranwen.org/cse/search?q={}&click=1&s=18402225725594290780&nsid='.format(title), headers=HEADERS)
    # with open('bb.html', 'w') as f:
    #     f.write(res.content.decode(encoding='utf-8'))
    body = etree.HTML(res.content)
    try:
        img_url = body.xpath('//img[@class="result-game-item-pic-link-img"]/@src')[0]
    except IndexError:
        print('{} wrong in {}'.format(index, title))
        return
    img_req = requests.get(img_url)
    with open('./images/' + str(index) + 's.jpg', 'wb') as wf:
        wf.write(img_req.content)
    print('{} done {}'.format(index, title))


@time_clock
def record_title_index():
    """
    取出有download url的信息
    :return:
    """
    with codecs.open('download_url', 'r', encoding='utf-8') as rf:
        title_list = []
        tls = rf.readlines()
        for tl in tls:
            title, url = tl.split(',')
            if len(url) > 2:
                title_list.append(title + ',' + url)

    # for index, title in enumerate(title_list, start=1):
    #     get_img(index, title)
    #     time.sleep(random.randint(0, 12))
    with open('./images/title_list.txt', 'w') as wf:
        wf.write(''.join(title_list))


@time_clock
def download_novel():
    """
    去文件中，下载url的的小说
    :return:
    """
    with open('./images/title_list.txt', 'r') as rf:
        for index, line in enumerate(rf.readlines(), start=1):
            if index < 1:
                continue
            title, url = line.strip().split(',')
            try:
                res = requests.get(url, headers=HEADERS)
            except requests.exceptions.ConnectionError:
                print('wrong in {}, {}'.format(index, title))
                continue
            with codecs.open('./book/' + str(index) + '.txt', 'w', encoding='utf-8') as wf:
                wf.write(res.text)
            print('done with {}, {}'.format(index, title))
            time.sleep(random.randint(0, 12))


@time_clock
def product_txt_split_rule(start=None, end=None, file_path='./'):

    file_list = [file_path + str(i) for i in sorted(map(int, os.listdir(file_path)))]
    rule_list = []
    for i, file_name in enumerate(file_list[start:end], start=1):
        with open(file_name, 'rb') as rf:
            title = pickle.load(rf)['title']
        s = "./book/{i}.txt,{title},{i},./book/chapter/{i:0>2}, ".format(i=i, title=title)
        rule_list.append(s)
    with open('txt_split_rule.txt', 'w') as wf:
        wf.write('\n'.join(rule_list))


@time_clock
def bbb(file):
    with open(file, 'r') as rf:
        # res_list = rf.readlines()
        for line in rf.readlines():
            var_list = line.strip('\n').split(',')
            print(var_list)
            split_txt(*var_list)

            # res_list = res_list[1:]
        # rf.write('\n'.join(res_list))


if __name__ == '__main__':
    # download_novel()
    # import os
    # import pickle
    # info_list = os.listdir('./info/')
    # for info in info_list:
    #     with open('./info/' + info, 'rb') as rf:
    #         res = pickle.load(rf)
    #         print(res.get('category'))
    test_ll = ['./book/1.txt', '逆鳞', r'第.*?卷', 1, './book/chapter/01', r'！']

    tt_ll = [
        # ['./book/2.txt', '择天记', [r'第.*?卷', r'正文'], 2, './book/chapter/02', r' '],
        # ['./book/3.txt', '妖神记', r'第.*?卷', 3, './book/chapter/03', r' '],
        # ['./book/4.txt', '大主宰', r'正文', 4, './book/chapter/04', r' '],
        # ['./book/5.txt', '高术通神', r'正文', 5, './book/chapter/05', r' '],
        # ['./book/6.txt', '绝世战魂', r'正文', 6, './book/chapter/06', r' '],
        # ['./book/7.txt', '凌天战尊', r'正文', 7, './book/chapter/07', r' '],
        # ['./book/8.txt', '重生之都市修仙', r'第.*?卷', 8, './book/chapter/08', r' '],
    ]

    # for t in tt_ll:
    #     split_txt(*t)
    # product_txt_split_rule(file_path='./info/')
    bbb('./txt_split_rule.txt')
