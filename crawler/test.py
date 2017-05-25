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
    # bbb('./txt_split_rule.txt')
