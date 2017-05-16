# -*- coding:utf-8 -*-
"""
协程爬虫模块
这个模块就为了两个功能
1 处理info页面：接收一个url，去该页面收集所有url，将url带上index传入redis
2 处理detail页面：接收[index, url]，去该页面采集内容，然后按index的名字存到本地

对于parse rule来讲，如果存入的是list形式，就代表要将其爬取部分转换了带html标签的
--------------------------------------
模块功能细化，将两个功能独立成不同的子模块

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


class Crawler(object):  # 父类只提供爬取的逻辑，子类自己定义储存方式

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5, store_path='./'):
        self.loop = loop or asyncio.get_event_loop()
        self.parse_rule = parse_rule
        self.urls = urls
        self.max_tasks = max_tasks
        self.session = aiohttp.ClientSession(loop=self.loop, headers=HEADERS)
        self.q = Queue(loop=self.loop)
        self.index_url_flag = False

        if isinstance(self.urls, list):
            for url in self.urls:
                if isinstance(url, list):  # 传入要求格式是[index, url]
                    self.index_url_flag = True   # 判断url是否带index
                self.add_url(url)
        else:
            self.add_url(self.urls)

        self.store_path = store_path
        if not os.path.exists(self.store_path):
            os.mkdir(self.store_path)

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
                    res['id'] = index
                else:
                    url = await self.q.get()
                res = res.update(await self.fetch(url))
                self.q.task_done()
                self.store(res)
                LOGGER.debug('done with {}'.format(url))
        except asyncio.CancelledError:
            pass

    def store(self, res):  # 子类重写这个方法就行了
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


class InfoCrawler(Crawler):  # 普通信息保存到本地，然后url保存到redis

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5, store_path='./', url_index=None):
        super(InfoCrawler, self).__init__(urls, parse_rule, loop, max_tasks, store_path=store_path)
        self.redis = redis.StrictRedis()
        self.url_index = url_index

    def store(self, res):  # 因为现在这一步只会用在info页面
        _url_list = {}
        _file_name = res['title']
        _url_list[_file_name] = res['urls']
        res.pop('urls')

        with open(self.store_path + _file_name, 'wb') as wf:  # 保存info信息到本地
            pickle.dump(res, wf)

        if self.url_index is None:
            raise RuntimeError('url index is none')
        for k, v in _url_list.items():  # 存url进redis
            if isinstance(v, list):
                for item in v:  # 可以直接在这里为url添加序号
                    item = str(self.url_index) + '!' + item  # 这样在取出的时候直接split就可以得到序号和url了
                    self.redis.rpush(k, item)
            else:
                self.redis.rpush(k, v)


class DetailCrawler(Crawler):  # 传入的url形式必须是[index, url]

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5, store_path='./'):
        super(DetailCrawler, self).__init__(urls, parse_rule, loop, max_tasks, store_path)

    def store(self, res):  # 按index的名字,保存正文和章节名到本地
        if isinstance(res, dict):
            if 'id' in res:
                _file_path = self.store_path + str(res['id'])
            else:
                _file_path = self.store_path + 'tmp'
            with open(_file_path, 'wb') as wf:
                pickle.dump(res, wf)
        else:
            LOGGER.warning('wrong type in serialization')


def run_crawler(crawler):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.crawl())
    crawler.close()
    loop.close()


if __name__ == '__main__':

    # DETAIL_RULE = {
    #     'chapter': '//div[@class="bookname"]/h1/text()',
    #     'content': ['//div[@id="content"]', ],
    # }
    # URLS = ['http://www.ranwen.org/files/article/56/56048/10973525.html',
    #         'http://www.ranwen.org/files/article/56/56048/11281440.html',]

    URLS = 'http://www.ranwen.org/files/article/56/56048/'
    RULE = {'urls': '//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href'}

    # t_q = Thread_queue()
