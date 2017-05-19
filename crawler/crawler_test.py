import asyncio
from contextlib import contextmanager
import io
import os
import logging
import socket
import unittest
from functools import partial
import pickle

from aiohttp import ClientError, web

from crawler.my_crawler import DetailCrawler


@contextmanager
def capture_logging():

    logger = logging.getLogger('crawling')
    level = logger.level
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(io.StringIO())
    logger.addHandler(handler)

    class Messages:
        def __contains__(self, item):
            return item in handler.stream.getvalue()

        def __repr__(self):
            return repr(handler.stream.getvalue())

    try:
        yield Messages()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(level)


class TestCrawler(unittest.TestCase):

    def setUp(self):
        if os.path.exists('./tmp'):
            os.remove('./tmp')

        self.loop = asyncio.new_event_loop()
        # self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(None)  # ? why not set self.loop

        def close_loop():
            self.loop.stop()
            self.loop.run_forever()
            self.loop.close()
        self.addCleanup(close_loop)  # 传入的func会在test完成后执行

        self.port = self._find_unused_port()
        self.app_url = 'http://127.0.0.1:{}'.format(self.port)
        self.app = self.loop.run_until_complete(self._create_server())
        self.crawler = None

    def _find_unused_port(self):  # 如果内部没用self的东西，就会被建议写成static method
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 协议，形式
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    async def _create_server(self):
        app = web.Application(loop=self.loop)
        handler_factory = app.make_handler(debug=True)  # 源码中调用了route.freeze,现把他注释掉了
        srv = await self.loop.create_server(
            handler_factory, '127.0.0.1', self.port)

        self.addCleanup(partial(self.loop.run_until_complete, handler_factory.finish_connections()))

        self.addCleanup(srv.close)
        return app

    def add_handler(self, url, handler):  # 绑定handle到router
        self.app.router.add_route('GET', url, handler)

    def add_page(self, url='/', links=None, body=None, content_type=None):  # 按需求添加page
        if not body:
            text = ''.join('<a href="{}"></a>'.format(link) for link in links or [])
            body = text.encode('utf-8')

        if content_type is None:
            content_type = 'text/html; charset=utf-8'

        async def handler(req):
            await req.read()
            return web.Response(body=body, headers=[
                ('CONTENT-TYPE', content_type)])

        self.add_handler(url, handler)
        return self.app_url + url

    def add_redirect(self, url, link):

        async def handler(_):
            raise web.HTTPFound(link)

        self.add_handler(url, handler)
        return self.app_url + url

    def crawl(self, urls=None, *args, **kwargs):
        if self.crawler:
            self.crawler.close()
        if urls is None:
            urls = [self.app_url]
        self.crawler = DetailCrawler(urls, parse_rule={'a': '//a/@href'}, loop=self.loop, *args, **kwargs)
        self.addCleanup(self.crawler.close)
        self.loop.run_until_complete(self.crawler.crawl())

    def test_link(self):
        url = self.add_page('/', ['/bar'])
        self.crawl(url)
        self.assertTrue(os.path.exists('./tmp'))
        with open('./tmp', 'rb') as f:
            res = pickle.load(f)
        self.assertEqual('/bar', res['a'])


if __name__ == '__main__':
    unittest.main()


