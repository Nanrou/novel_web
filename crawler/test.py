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


if __name__ == '__main__':
    ps, pr = Pipe()
    eee = Event()
    #
    # def sl():
    #     loop = asyncio.get_event_loop()
    #     bbb = loop.run_until_complete(sf())
    #     loop.close()
    #     return bbb
    #
    # print(sl())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(test())
    # loop.close()
    from . import my_request
