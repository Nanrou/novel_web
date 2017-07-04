# -*- coding:utf-8 -*-
"""
协程爬虫模块
这个模块就为了两个功能
1 处理info页面：接收一个url，去该页面收集所有url，将url带上index传入redis
2 处理detail页面：接收[index, url]，去该页面采集内容，然后按index的名字存到本地

对于parse rule来讲，如果存入的是list形式，就代表要将其爬取部分转换了带html标签的
--------------------------------------
5.17
模块功能细化，将两个功能独立成不同的子模块
--------------------------------------
5.19
针对detail模块，添加一个confirm request的装饰器
但是想了想，这个确认应该包在保存后
--------------------------------------
5.20
更正了超时的异常捕捉
修正了work中对爬取失败的处理
--------------------------------------
5.23
新增对应网站的爬取方式
--------------------------------------
5.25
再降耦合，把协程下载分出来
--------------------------------------
7.3
重构最核心部分

"""

import os.path
import pickle
import asyncio
import random
from asyncio import Queue
from functools import wraps
from async_timeout import timeout
import time
import codecs
from collections import namedtuple


import aiohttp
from lxml import etree
from lxml.etree import XPathError
import redis
import requests

from crawler.utls.my_logger import MyLogger
from crawler.crawler.my_exception import FetchError


"""
约定
XPath的规则dict
info表的表头为
{'title', 'update_time', 'image', 'resume', 'author', 'category', 'status'}
则对应的xpath规则必须有包含这些
{
    'title': ,
    'update_time': ,
    'image_url': , 这个要用其他模块下载
    'resume': ,
    'author': ,
    'category': ,
    'status': ,
    'novel_url': , 这个要用其他模块下载
}
"""

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}

LOGGER = MyLogger('crawler_log')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AsyncCrawlerBase(object):
    """
    异步下载主逻辑
    接收urls，然后就安排工人下载
    要求传入的urls必须是name_tuple,['name', 'url']
    """

    def __init__(self, urls, loop=None, max_tasks=5, store_path='./'):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._loop = loop
        self._urls = urls
        self._max_tasks = max_tasks
        self._session = aiohttp.ClientSession(loop=self._loop, headers=HEADERS)
        self._q = Queue(loop=self._loop)

        if isinstance(self._urls, list):
            for url in self._urls:
                self.add_url(url)
        else:
            self.add_url(self._urls)

        assert isinstance(store_path, str) is True, 'must input store_path'
        if not store_path.endswith('/'):  # 确保储存位置存在
            store_path += '/'
        self._store_path = os.path.join(BASE_DIR, store_path)
        if not os.path.exists(self._store_path):
            os.mkdir(self._store_path)

    def add_url(self, url):  # 塞url到队列里
        self._q.put_nowait(url)

    async def crawl(self):  # 生产工人
        workers = [asyncio.Task(self.work(), loop=self._loop)
                   for _ in range(self._max_tasks)]
        await self._q.join()
        for w in workers:
            w.cancel()

    async def work(self):  # 工人工作
        try:
            while True:
                asyncio.sleep(random.randint(1, 3))
                name, url = await self._q.get()  # 在这里拆包
                body = await self.my_request(url)
                if body is None:
                    LOGGER.warning('download None in [{}]'.format(url))
                else:
                    try:
                        res = self.fetch(body)
                    except FetchError as e:  # 捕捉剥取异常
                        LOGGER.warning('{} in [{}]'.format(e, url))
                    else:
                        self.store(name, res)
                self._q.task_done()
                LOGGER.debug('done with {}'.format(url))
        except asyncio.CancelledError:
            pass

    async def my_request(self, url):  # 发送请求
        try:
            with timeout(3, loop=self._loop):
                async with self._session.get(url) as resp:
                    if resp.status != 200:
                        LOGGER.warning('get an invalid response in {}'.format(url))
                        return
                    return await resp.text()
        except asyncio.TimeoutError:  # 注意捕捉的类别
            LOGGER.warning('timeout in {}'.format(url))
        finally:
            return

    def store(self, name, res):
        _file_name = os.path.join(self._store_path, name)
        with open(_file_name, 'w') as wf:
            pickle.dump(res, wf)

    def fetch(self, body):
        raise RuntimeError('must rewrite fetch part')

    def close(self):
        self._session.close()


class XpathCrawler(AsyncCrawlerBase):
    """
    加了根据xpath规则来剥取的方法，和保存方法
    """
    def __init__(self, urls, parse_rule, *args, **kwargs):
        """

        :param urls: 接收的url
        :param parse_rule: 接收dict来作为爬取规则
        :param args:
        :param kwargs:
        """
        super(XpathCrawler, self).__init__(urls, *args, **kwargs)
        assert isinstance(parse_rule, dict) is True, 'must input dict'
        self._parse_rule = parse_rule

    def fetch(self, body):  # 分析页面抓取
        page_body = etree.HTML(body)
        res = {}
        for k, v in self._parse_rule.items():
            try:
                res[k] = page_body.xpath(v)[0]
            except XPathError or IndexError:  # 抛出剥取异常
                raise FetchError('wrong xpath syntax [{}]'.format(k))
        return res


class DownloadCrawler(AsyncCrawlerBase):  # 下载模块
    def __init__(self, name_tuple_urls, *args, **kwargs):
        super(DownloadCrawler, self).__init__(name_tuple_urls, *args, **kwargs)

    def fetch(self, body):  # 下载模块的fetch直接返回response本体就行了
        return body


class ImageDownload(DownloadCrawler):  # 图片下载模块
    def __init__(self, name_tuple_urls, store_path='./image/', *args, **kwargs):
        super(ImageDownload, self).__init__(name_tuple_urls, store_path=store_path, *args, **kwargs)

    def store(self, name, res):
        _file_name = os.path.join(self._store_path, name+'s.jpg')
        with open(_file_name, 'wb') as wf:
            wf.write(res)


class NovelDownload(DownloadCrawler):  # 小说下载模块
    def __init__(self, name_tuple_urls, store_path='./novel/', *args, **kwargs):
        super(NovelDownload, self).__init__(name_tuple_urls, store_path=store_path, *args, **kwargs)

    def store(self, name, res):
        _file_name = os.path.join(self._store_path, name+'.txt')
        with codecs.open(_file_name, 'w', encoding='utf-8') as wf:
            wf.write(res)


def run_crawler(crawler):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.crawl())
    crawler.close()
    loop.close()


def search_novel(index, title, url, store_path='./'):
    """
    去url那个网站，搜名为title的小说，然后保存info信息到store_path，再返回下载小说的download url
    :param index:
    :param title:
    :param url:
    :param store_path:
    :return:
    """

    header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}

    payload = {"searchkey": title.encode(encoding='gbk'), "ct": "2097152", "si": "ranwenw.com",
               "sts": "ranwenw.com"}
    rule = {
        'download_url': '//div[@id="maininfo"]/div[@id="info"]/p[last()]/a/@href',
        'title': '//div[@id="maininfo"]/div[@id="info"]/h1/text()',
        'author': '//div[@id="maininfo"]/div[@id="info"]/p[1]/text()',
        # 'status': '//div[@id="maininfo"]/div[@id="info"]/p[2]/text()',
        'category': '//div[@class="con_top"]/a[2]/text()',
        'resume': '//div[@id="maininfo"]/div[@id="intro"]/p[1]/text()',
        # 'img_url': '//div[@id="fmimg"]//img/@src',
    }
    try:
        r = requests.post(url, data=payload, headers=header)
    except requests.exceptions.ConnectionError:
        LOGGER.warning('out try in {}'.format(title))
        return

    body = etree.HTML(r.content)
    res = {}

    try:
        tmp = body.xpath('//div[@id="content"]/table[@class="grid"]/caption/text()')
        if tmp:
            LOGGER.debug('search failed: {}'.format(title))
            return
    except XPathError:
        pass

    try:
        for k, v in rule.items():
            _value_list = body.xpath(v)
            if len(_value_list) == 0:
                LOGGER.warning('wrong xpath {} in {}'.format(k, title))
            elif len(_value_list) == 1:
                res[k] = _value_list[0]
            else:
                LOGGER.warning('too many item {} in {}'.format(k, title))

    except XPathError:
        LOGGER.debug('{} not found'.format(title))
        return

    else:
        try:
            download_url = res['download_url']
        except KeyError:
            LOGGER.debug('{} not found'.format(title))
            return

        res.pop('download_url')

        res['_status'] = '连载中'
        res['img_url'] = ''

        with codecs.open(store_path + str(index), 'wb') as wf:
            pickle.dump(res, wf)

        if not download_url.startswith('http://'):
            download_url = 'http://www.ranwenw.com' + download_url
        return download_url


if __name__ == '__main__':

    DETAIL_RULE = {
        'title': '//div[@class="con_top"]/a[3]/text()',
        'chapter': '//div[@class="bookname"]/h1/text()',
        'content': ['//div[@id="content"]', ],
    }
    DETAIL_URLS = [[0, 'http://www.ranwen.org/files/article/56/56048/10973525.html'],
                   [1, 'http://www.ranwen.org/files/article/56/56048/11281440.html'],]

    INFO_URLS = 'http://www.ranwen.org/files/article/19/19388/'
    INFO_RULE = {
        'urls': '//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href',
        'title': '//div[@id="maininfo"]/div[@id="info"]/h1/text()',
        'author': '//div[@id="maininfo"]/div[@id="info"]/p[1]/text()',
        'status': '//div[@id="maininfo"]/div[@id="info"]/p[2]/text()',
        'category': '//div[@class="con_top"]/a[2]/text()',
        'resume': '//div[@id="maininfo"]/div[@id="intro"]/p[1]/text()',
        'img_url': '//div[@id="fmimg"]/img/@src',
    }
    SEARCH_URL = 'http://www.ranwenw.com/modules/article/search.php'
