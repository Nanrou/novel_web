# -*- coding:utf-8 -*-

import asyncio
from asyncio import Queue
import aiohttp
from lxml import etree
import logging
from async_timeout import timeout


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
)

LOGGER = logging.getLogger('')


class Crawler(object):

    def __init__(self, url_lists, parse_rule=None, loop=None, max_tasks=5):
        self.loop = loop or asyncio.get_event_loop()
        self.parse_rule = parse_rule
        self.url_lists = url_lists
        self.max_tasks = max_tasks
        self.session = aiohttp.ClientSession(loop=self.loop, headers=HEADERS)
        self.q = Queue(loop=self.loop)
        for url in url_lists:
            self.add_url(url)

    def __setattr__(self, key, value):
        return object.__setattr__(self, key, value)

    def add_url(self, url):
        self.q.put_nowait(url)

    async def work(self):
        try:
            while True:
                url = await self.q.get()
                res = await self.fetch(url)
                self.q.task_done()
                LOGGER.debug('done with {}'.format(url))
                return res  # 看怎么返回数据
        except asyncio.CancelledError:
            pass

    async def crawl(self):
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        await self.q.join()
        for w in workers:
            w.cancel()

    async def fetch(self, url):
        if self.parse_rule is None:
            raise Exception('must input parse_rule')
        page_body = await self.my_request(url)
        if page_body:
            page_body = etree.HTML(page_body)
            res = {}
            for k, v in self.parse_rule.items():
                try:
                    res[k] = etree.tounicode(page_body.xpath(v)[0])
                except IndexError:
                    LOGGER.debug('wrong xpath in {}'.format(url))
            return res
        else:
            LOGGER.debug('invalid page body in {}'.format(url))
            return

    async def my_request(self, url):
        try:
            with timeout(5, loop=self.loop):
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        LOGGER.debug('get an invalid response in {}'.format(url))
                        return
                    return await resp.text()
        except RuntimeError:
            LOGGER.debug('timeout in {}'.format(url))
        return

    def close(self):
        self.session.close()


if __name__ == '__main__':
    RULE = {
        'chapter': '//div[@class="bookname"]/h1',
        'content': '//div[@id="content"]',
    }
    URLS = ['http://www.ranwen.org/files/article/56/56048/10973525.html',]

    loop = asyncio.get_event_loop()
    crawler = Crawler(url_lists=URLS)
    crawler.parse_rule = RULE
    loop.run_until_complete(crawler.crawl())
    crawler.close()
    loop.close()
