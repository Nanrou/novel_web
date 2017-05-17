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


if __name__ == '__main__':

    from functools import wraps

    def confirm(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            print('i am wrapper')
            return func(self, *args, **kwargs)
        return wrapper


    class Test(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b

        @confirm
        def run(self):
            print(self.a + self.b)

    t = Test(1, 2)
    t.run()
