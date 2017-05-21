# -*- coding:utf-8 -*-


import aiohttp
import asyncio
from lxml import etree

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

import pickle
import pprint

import os
from multiprocessing import Process, Pipe, Event
from threading import Event, Thread
import queue
import asyncio
import time
import random


async def sf():
    ll = []
    i = 0
    while True:
        asyncio.sleep(random.randint(1, 5))
        print('i am %s' % i)
        ll.append(i)
        i += 1
        if i > 20:
            break
    return ll


def gf(p, e):
    while True:
        e.wait()
        print('get {}'.format(p.recv()))
        if p.recv() == -1:
            break
        e.clear()


def producte_cate():
    category = ['玄幻修仙', '科幻网游', '都市重生', '架空历史', '恐怖言情', '全本小说']
    cate = ['xuanhuan', 'kehuan', 'dushi', 'jiakong', 'kongbu', 'quanben']
    res = []
    for i in range(len(cate)):
        res.append({'id': i+1, 'category': category[i], 'cate': cate[i]})
    return res


class Parent(object):
    def __init__(self, a):
        self.a = a

    async def run(self, b):
        self.a += b
        print(self.a)

    async def work(self):
        asyncio.sleep(2)
        await self.run(2)


if __name__ == '__main__':
    import re
    import codecs

    title_rule = re.compile(r'    第*?章')

    with codecs.open('test/test/test.txt', 'r', encoding='utf-8') as f:
        ls = f.readlines()
        w_flag = True
        for index, line in enumerate(ls):
            if re.match(r'    第.?章', line):
                if w_flag:
                    start_index = index
                    chapter_title = line.strip()
                    w_flag = False
                else:
                    end_index = index - 2
                    with open(chapter_title + '.txt', 'w') as wf:
                        wf.write(''.join(ls[start_index:end_index]).replace('\r\n\r\n', '<br/>'))
                    # print(''.join(ls[start_index:end_index]))
                    w_flag = True

            if index > 150:
                break




