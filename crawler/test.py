import aiohttp
import asyncio
from lxml import etree

URL = 'http://www.ranwen.org/files/article/56/56048/10973525.html'

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            page = await resp.text()
            page = etree.HTML(page)
            content = page.xpath('//div[@class="bookname"]/h1')[0]
            print(type(content))
            print(etree.tounicode(content))

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test())

import pickle
import pprint

import os
from multiprocessing import Process, Pipe


def send(p):
    p.send('m t f')
    p.close()


def talk(p):
    p.send('?????????')
    reply = p.recv()
    print('talker got: {}'.format(reply))

if __name__ == '__main__':
    dd = {'a': 1, 'b': 2}

    (con1, con2) = Pipe()
    sender = Process(target=send, name='send', args=(con1,))
    sender.start()
    print('con2 got {}'.format(con2.recv()))
    con2.close()

    (parent, child) = Pipe()
    child = Process(target=talk, name='talk', args=(child,))
    child.start()
    print('parent got', parent.recv())
    parent.send('bbbb')
    child.join()
    print('end')

