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
"""
import os.path
import pickle
import asyncio
import random
from async_timeout import timeout
from asyncio import Queue
from functools import wraps
import time
import codecs

import aiohttp
from lxml import etree
from lxml.etree import XPathError
import redis
import requests

from my_logger import MyLogger


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}

LOGGER = MyLogger('crawler_log')


class Crawler(object):  # 父类只提供爬取的逻辑，子类自己定义储存方式

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5, store_path='./'):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.parse_rule = parse_rule
        self.urls = urls
        self.max_tasks = max_tasks
        self.session = aiohttp.ClientSession(loop=self.loop, headers=HEADERS)
        self.q = Queue(loop=self.loop)
        self.redis = redis.StrictRedis()

        # tmp_urls = self.redis.smembers('tmp')
        # for tmp_url in tmp_urls:
        #     self.add_url(tmp_url)
        self.redis.delete('tmp')

        if isinstance(self.urls, list):
            for url in self.urls:
                # if isinstance(url, list):  # 传入要求格式是[index, url]
                #     self.index_url_flag = True   # 判断url是否带index
                self.add_url(url)
        else:
            self.add_url(self.urls)

        self.store_path = store_path if store_path.endswith('/') else store_path + '/'
        if not os.path.exists(self.store_path):
            os.mkdir(self.store_path)

    def __setattr__(self, key, value):
        return object.__setattr__(self, key, value)

    def __getattr__(self, item):
        return object.__getattribute__(item)

    def add_url(self, url):
        self.q.put_nowait(url)
        self.redis.sadd('tmp', url)

    async def work(self):
        try:
            while True:
                asyncio.sleep(random.randint(1, 3))
                url = await self.q.get()
                res = await self.fetch(url)
                self.q.task_done()
                if not res:  # res为空或者None，则不存
                    LOGGER.warning('wrong in {}'.format(url))
                    continue
                self.store(res)
                self.redis.srem('tmp', url)
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
        # if not isinstance(self.parse_rule, dict):
        #     raise Exception('must input parse_rule in dict')  # 异步怎么捕捉异常
        res = {}
        if isinstance(url, list):  # 如果带index就赋值到res里去
            index, url = url
            res['id'] = index
        page_body = await self.my_request(url)
        if page_body:
            page_body = etree.HTML(page_body)
            for k, v in self.parse_rule.items():
                _keep_html_flag = False
                _value_list = []
                if isinstance(v, list):  # 如果需要保持文本内的html标签
                    _keep_html_flag = True
                    v = v[0]  # 因为传进来的就是一个元素的list
                try:
                    for ele in page_body.xpath(v):
                        if _keep_html_flag:
                            _value_list.append(etree.tounicode(ele))
                        else:
                            _value_list.append(ele)
                except XPathError:
                    LOGGER.warning('wrong xpath syntax {} in {}'.format(k, url))
                if len(_value_list) == 0:
                    LOGGER.warning('wrong xpath {} in {}'.format(k, url))
                elif len(_value_list) == 1:
                    res[k] = _value_list[0]
                else:
                    res[k] = _value_list
            return res  # 增加一个去除头尾标签的功能
        else:
            # LOGGER.warning('invalid page body in {}'.format(url))
            # return res.update({'title': 'error', 'chapter': 'error', 'content': 'error'})
            return

    async def my_request(self, url):
        try:
            with timeout(3, loop=self.loop):
                async with self.session.get(url) as resp:
                    if resp.status != 200:
                        LOGGER.warning('get an invalid response in {}'.format(url))
                        return
                    return await resp.text()
        except asyncio.TimeoutError:  # 注意捕捉的类别
            LOGGER.warning('timeout in {}'.format(url))
        finally:
            return

    def close(self):
        # with open('my.ini', 'ab') as wf:
        #     dd = {'doc_id': self.doc_id}
        #     pickle.dump(dd, wf)
        self.session.close()


class InfoCrawler(Crawler):  # 普通信息保存到本地，然后url保存到redis

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5, store_path='./', book_index=None):
        """
        :param urls:
        :param parse_rule:
        :param loop:
        :param max_tasks:
        :param store_path:
        :param book_index: 用于指定info的id
        """
        super(InfoCrawler, self).__init__(urls, parse_rule, loop, max_tasks, store_path=store_path)
        if book_index is not None:
            assert book_index is int
            self.book_index = book_index
        elif os.path.exists('my.ini'):
            with open('my.ini', 'rb') as rf:
                r = pickle.load(rf)
                self.book_index = r['book_index']
        else:
            self.book_index = 1

    def store(self, res):  # 因为现在这一步只会用在info页面
        _url_list = {}
        _file_name = str(self.book_index)
        _url_list[_file_name] = res['urls']
        res.pop('urls')

        with open(self.store_path + _file_name, 'wb') as wf:  # 保存info信息到本地
            pickle.dump(res, wf)

        url_index = self.book_index * 10000

        for k, v in _url_list.items():  # 存url进redis
            if isinstance(v, list):
                for item in v:  # 可以直接在这里为url添加序号
                    item = str(url_index) + '!' + item  # 这样在取出的时候直接split就可以得到序号和url了
                    self.redis.rpush(k, item)
                    url_index += 1
            else:
                self.redis.rpush(k, v)

        self.book_index += 1

    def close(self):
        with open('my.ini', 'wb') as wf:
            r = {'book_index': self.book_index}
            pickle.dump(r, wf)
        super(InfoCrawler, self).close()


def confirm_request(func):  # 再次确认爬取是否成功
    @wraps(func)
    def wrapper(self, url):
        index, u = url
        self.redis.sadd('tmp', str(index) + '!' + u)
        res = func(self, url)
        self.redis.srem('tmp', str(index) + '!' + u)
        return res
    return wrapper


class DetailCrawler(Crawler):  # 传入的url形式必须是[index, url]，不带index的话，则保存为tmp

    def __init__(self, urls, parse_rule, loop=None, max_tasks=5, store_path='./'):
        super(DetailCrawler, self).__init__(urls, parse_rule, loop, max_tasks, store_path)
        self.final_store_path = None

    def store(self, res):  # 按index的名字,保存正文和章节名到本地
        try:
            store_path = self.store_path + res['title'] + '/'
            if not os.path.exists(store_path):
                os.mkdir(store_path)
                self.final_store_path = store_path
        except KeyError:
            LOGGER.debug('title not found')
            store_path = self.store_path
        if 'id' in res:
            _file_path = store_path + str(res['id'])
        else:
            _file_path = self.store_path + 'tmp'
        with open(_file_path, 'wb') as wf:
            pickle.dump(res, wf)  # res里面是有带id的url

    # @confirm_request  # 异步的装饰器和普通的一样
    # async def fetch(self, url):
    #     return await super(DetailCrawler, self).fetch(url)  # 调用要记得返回


def run_crawler(crawler):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawler.crawl())
    crawler.close()
    loop.close()


class ImageDownload(Crawler):
    pass


def image_download(index, url, store_path='./novel_site/images/'):
    if not store_path.endswith('/'):
        store_path += '/'
    if not os.path.exists(store_path):
        os.mkdir(store_path)
    res = requests.get(url)
    filename = store_path + str(index) + 's.jpg'
    with open(filename, 'wb') as wf:
        wf.write(res.content)
    return filename[2:]


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

        res['status'] = '连载中'
        res['img_url'] = ''

        with codecs.open(store_path + str(index), 'wb') as wf:
            pickle.dump(res, wf)

        if not download_url.startswith('http://'):
            download_url = 'http://www.ranwenw.com' + download_url
        return download_url


# res = requests.get('http://www.ranwenw.com/modules/article/txtarticle.php?id=52', headers=HEADER)
# with codecs.open('nilin.txt', 'w', encoding='utf-8') as f:
#     f.write(res.text)


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

    # infoc = InfoCrawler(urls=INFO_URLS, parse_rule=INFO_RULE, store_path='./bbb/')
    # run_crawler(infoc)

    # detailc = DetailCrawler(urls=DETAIL_URLS, parse_rule=DETAIL_RULE, store_path = './test')
    # run_crawler(detailc)
    # print(detailc.store_path)
    SEARCH_URL = 'http://www.ranwenw.com/modules/article/search.php'
