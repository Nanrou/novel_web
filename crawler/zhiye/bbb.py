# -*- coding:utf-8 -*-

import sys
import codecs
from collections import namedtuple

sys.path.append('F:\\Git\\novel_web')


import requests
from lxml import etree

from crawler.crawler.my_crawler import XpathCrawler
from crawler.crawler.my_crawler import run_crawler

DATA = {
    'jl': '珠海',
    'kw': 'python',
    'sm': '0',
    'p': '1',
    'isfilter': '0',
    'fl': '766',
    'isadv': '0',
    'sb': '2'
}

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN'
}

COOKIES = {'td_cookie': '1636681570'}

URL = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E7%8F%A0%E6%B5%B7&kw=python&sm=0&p=1&isfilter=0&fl=766&isadv=0&sb=2'
DURL = 'http://jobs.zhaopin.com/419981221250268.htm?ssidkey=y&ss=201&ff=03&sg=1e726a5b81a74d478ad9f0f7a6447b0a&so=1'


def download(url):
    response = requests.get(url, headers=HEADERS)

    with codecs.open('ddd.html', 'w', encoding='utf-8') as f:
        f.write(response.content.decode(encoding='utf-8'))


class DownloadUrl(XpathCrawler):
    def fetch(self, body):
        page_body = etree.HTML(body)
        res = []
        # assert 'title' in self._parse_rule is True, 'wrong in title'
        # assert 'url' in self._parse_rule is True, 'wrong in url'
        urls = page_body.xpath(self._parse_rule['url'])
        for i, title in enumerate(page_body.xpath(self._parse_rule['title'])):
            t = title.text
            u = urls[i]
            res.append([t, u])
            # res.append(','.join([title.text, page_body.xpath(self._parse_rule['url'])[i]]))
        print('out fetch', res)
        return res


class DownloadComment(XpathCrawler):
    async def fetch(self, body):
        page_body = etree.HTML(body)
        res = {}
        for k, v in self._parse_rule.items():
            try:
                v = page_body.xpath(v)
                if len(v) > 1:
                    res[k] = '\n'.join(i.text for i in v)
                else:
                    res[k] = v[0].text.strip('\xa0')
            except IndexError:  # 抛出剥取异常
                res[k] = 'wrong xpath'
        return res



ZHILIAN_INFO_RULE = {
    'title': '//table[@class="newlist"]/tr/td[@class="zwmc"]/div/a',
    'url': '//table[@class="newlist"]/tr/td[@class="zwmc"]/div/a/@href'
    }

ZHILIAN_DETAIL_RULE = {
    'title': '//div[@class="inner-left fl"]/h1',
    'company': '//div[@class="inner-left fl"]/h2/a',
    'salary': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[1]/strong',
    'work_des': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[2]/strong/a',
    'education': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[6]/strong',
    'content': '//div[@class="tab-inner-cont"]/p//span',
    }


def fetch():
    with codecs.open('ccc.html', 'r', encoding='utf-8') as rf:
        body = etree.HTML(rf.read())
        res = {}
        for k, v in ZHILIAN_DETAIL_RULE.items():
            v = body.xpath(v)
            if len(v) > 1:
                res[k] = '\n'.join(i.text for i in v)
                    
            else:
                res[k] = v[0].text.strip('\xa0')
            
        print(res)
if __name__ == '__main__':
    # fetch()
    # download(URL)

    import asyncio
    loop = asyncio.get_event_loop()
    dd = DownloadUrl(URL, ZHILIAN_INFO_RULE, loop=loop)
    loop.run_until_complete(dd.crawl())
    dd.close()
    # import aiohttp
    # import asyncio
    #
    # async def ccc(session, url):
    #     async with session.get(url) as resp:
    #         return await resp.text()
    #
    # async def main(loop):
    #     async with aiohttp.ClientSession(loop=loop, headers=HEADERS) as session:
    #         html = await ccc(session, URL)
    #         print(html)
    #
    #
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main(loop))
    #

