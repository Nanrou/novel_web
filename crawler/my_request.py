# -*- coding:utf-8 -*-
"""
协程爬虫模块



"""
import os.path
import pickle
import logging
import asyncio
from async_timeout import timeout
from asyncio import Queue

import aiohttp
from lxml import etree
import redis


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
)

LOGGER = logging.getLogger('')  # 改成持久化


class Crawler(object):

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5,
                 stone_in_redis=False, doc_id=0, stone_path='./'):
        self.loop = loop or asyncio.get_event_loop()
        self.parse_rule = parse_rule
        self.url_lists = urls
        self.max_tasks = max_tasks
        self.session = aiohttp.ClientSession(loop=self.loop, headers=HEADERS)
        self.q = Queue(loop=self.loop)
        self.index_url_flag = False
        if isinstance(urls, list):
            for url in urls:
                if isinstance(url, list):
                    self.index_url_flag = True   # 判断url是否带index
                self.add_url(url)
        else:
            self.add_url(urls)

        self.stone_in_redis = stone_in_redis
        if self.stone_in_redis:
            self.redis = redis.StrictRedis()

        if doc_id:  # 应该设计为计数
            assert isinstance(doc_id, int) is True
            self.doc_id = doc_id
        elif os.path.exists('my.ini'):
            with open('my.ini', 'rb') as rf:
                ff = pickle.load(rf)
                self.doc_id = ff['doc_id']
        else:
            self.doc_id = doc_id

        self.stone_path = stone_path

    def __setattr__(self, key, value):
        return object.__setattr__(self, key, value)

    def add_url(self, url):
        self.q.put_nowait(url)

    async def work(self):
        try:
            while True:
                res = {}
                if self.index_url_flag:
                    index, url = await self.q.get()
                    res['index'] = index
                else:
                    url = await self.q.get()
                res = res.update(await self.fetch(url))
                self.q.task_done()
                LOGGER.debug('done with {}'.format(url))
                # return res  # 看怎么返回数据
                if self.stone_in_redis:
                    self.stone_to_redis(res)
                else:
                    self.serialization(res)
        except asyncio.CancelledError:
            pass

    async def crawl(self):
        workers = [asyncio.Task(self.work(), loop=self.loop)
                   for _ in range(self.max_tasks)]
        await self.q.join()
        for w in workers:
            w.cancel()

    async def fetch(self, url):
        if isinstance(self.parse_rule, dict):
            raise Exception('must input parse_rule in dict')
        page_body = await self.my_request(url)
        if page_body:
            page_body = etree.HTML(page_body)
            res = {}
            for k, v in self.parse_rule.items():
                _keep_html_flag = False
                _value_list = []
                if isinstance(v, list):  # 如果需要保持文本内的html标签
                    _keep_html_flag = True
                    v = v[0]  # 因为传进来的就是一个元素的list
                for ele in page_body.xpath(v):
                    if _keep_html_flag:
                        _value_list.append(etree.tounicode(ele))
                    else:
                        _value_list.append(ele)
                if len(_value_list) == 0:
                    LOGGER.warning('wrong xpath in {}'.format(url))
                elif len(_value_list) == 1:
                    res[k] = _value_list[0]
                else:
                    res[k] = _value_list
            return res  # 增加一个去除头尾标签的功能
        else:
            LOGGER.warning('invalid page body in {}'.format(url))
            return

    async def my_request(self, url):
        try:
            with timeout(5, loop=self.loop):
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        LOGGER.warning('get an invalid response in {}'.format(url))
                        return
                    return await resp.text()
        except RuntimeError:
            LOGGER.warning('timeout in {}'.format(url))
        return

    def close(self):
        # with open('my.ini', 'ab') as wf:
        #     dd = {'doc_id': self.doc_id}
        #     pickle.dump(dd, wf)
        self.session.close()

    def serialization(self, res):  # 增加分类文件夹
        if isinstance(res, dict):
            if 'index' in res:
                _file_path = self.stone_path + str(res['index'])
                res.pop('index')
            else:
                _file_path = self.stone_path + str(self.doc_id)
            with open(_file_path, 'wb') as pf:
                pickle.dump(res, pf)
        else:
            LOGGER.warning('wrong type in serialization')

    def stone_to_redis(self, res):
        if isinstance(res, dict):
            for k, v in res.items():
                if isinstance(v, list):
                    for item in v:
                        self.redis.rpush(k, item)
                else:
                    self.redis.rpush(k, v)
        else:
            LOGGER.warning('wrong type in stone_to_redis')


def run_crawler(urls, parse_rule, loop=None, *args, **kwargs):
    loop = loop or asyncio.get_event_loop()
    crawler = Crawler(urls, parse_rule, loop, *args, **kwargs)
    loop.run_until_complete(crawler.crawl())
    crawler.close()
    loop.close()


if __name__ == '__main__':

    # RULE = {
    #     'chapter': '//div[@class="bookname"]/h1/text()',
    #     'content': ['//div[@id="content"]', ],
    # }
    # URLS = ['http://www.ranwen.org/files/article/56/56048/10973525.html',
    #         'http://www.ranwen.org/files/article/56/56048/11281440.html',]

    URLS = 'http://www.ranwen.org/files/article/56/56048/'
    RULE = {'urls': '//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href'}

    # t_q = Thread_queue()
    run_crawler(URLS, RULE)
