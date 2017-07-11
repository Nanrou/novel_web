# -*- coding:utf-8 -*-

import sys
import os
import codecs
from collections import namedtuple
import logging
import asyncio
import datetime
import pickle

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath('__file__')))))


import requests
from lxml import etree
from lxml.etree import XPathError

from crawler.crawler.my_crawler import XpathCrawler
from crawler.utls.my_logger import MyLogger
from crawler.utls.my_decorate import time_clock

LOGGER = MyLogger('zhiye')

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN'
}

COOKIES = {'td_cookie': '1636681570'}

DURL = 'http://jobs.zhaopin.com/419981221250268.htm?ssidkey=y&ss=201&ff=03&sg=1e726a5b81a74d478ad9f0f7a6447b0a&so=1'

ZHILIAN_INFO_RULE = {
    'title': '//table[@class="newlist"]/tr/td[@class="zwmc"]/div/a',
    'url': '//table[@class="newlist"]/tr/td[@class="zwmc"]/div/a/@href'
}

ZHILIAN_DETAIL_RULE = {
    'title': '//div[@class="fixed-inner-box"]/div/h1',
    'company': '//div[@class="fixed-inner-box"]/div/h2/a',
    'salary': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[1]/strong',
    'work_des': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[2]/strong/a',
    'content': '//div[@class="tab-inner-cont"]',
}

QIANCHENGWUYOU_INFO_RULE = {
    'title': '//div[@class="dw_table"]/div[@class="el"]/p/span/a/text()',
    'url': '//div[@class="dw_table"]/div[@class="el"]/p/span/a/@href',
    'pub_date': '//div[@class="dw_table"]/div[@class="el"]/span[@class="t5"]/text()',
}

QIANCHENGWUYOU_DETAIL_RULE = {
    'title': '//div[@class="cn"]/h1/text()',
    'company': '//div[@class="cn"]/p[@class="cname"]/a/text()',
    'salary': '//div[@class="cn"]/strong/text()',
    'work_des': '//div[@class="bmsg inbox"]/p[@class="fp"]/text()[2]',
    'content': '//div[@class="bmsg job_msg inbox"]/text()',
}


def download_html(url):
    response = requests.get(url, headers=HEADERS)
    content = response.content.decode(response.apparent_encoding).encode('utf-8').decode('utf-8')
    try:
        with open('hhh.html', 'w') as wf:
            wf.write(content)
    except UnicodeError:
        with codecs.open('hhh.html', 'w', encoding='utf-8') as wf:
            wf.write(content)


class ZHILIANDownloadUrl(XpathCrawler):
    def fetch(self, body):
        page_body = etree.HTML(body)
        res = []
        assert 'title' in self._parse_rule, 'wrong in title'
        assert 'url' in self._parse_rule, 'wrong in url'
        urls = page_body.xpath(self._parse_rule['url'])
        for i, title in enumerate(page_body.xpath(self._parse_rule['title'])):
            _t = title.xpath('string(.)')  # xpath('string(.)') 提取当前便签下的所有字符串
            _u = urls[i]
            res.append([_t, _u])
            # res.append(','.join([title.text, page_body.xpath(self._parse_rule['url'])[i]]))
        return res


class ZHILIANDownloadComment(XpathCrawler):
    def __init__(self, *args, **kwargs):
        super(ZHILIANDownloadComment, self).__init__(*args, **kwargs)
        self._file_num = 0

    def fetch(self, body):
        page_body = etree.HTML(body)
        res = {}
        for k, v in self._parse_rule.items():
            try:
                if k is 'content':
                    res[k] = page_body.xpath(v)[0].xpath('string(.)')\
                        .replace('\r\n', '').replace('\xa0', '').replace(' ', '')
                else:
                    res[k] = page_body.xpath(v)[0].text.replace('\xa0', '')
            except IndexError:  # 抛出剥取异常
                res[k] = 'wrong context xpath'
            except XPathError:  # 为什么这个异常没有捕捉到
                res[k] = 'other wrong xpath'
        return res

    def store(self, res):
        date_time = '{:%Y-%m-%d}'.format(datetime.datetime.today())
        folder_name = './' + date_time
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        # with open(folder_name + '/' + res.get('title'), 'wb') as wf:
        #     pickle.dump(res, wf)
        with open(folder_name + '/z' + str(self._file_num), 'wb') as wf:
            pickle.dump(res, wf)
        self._file_num += 1


class QCWYDownloadURL(XpathCrawler):
    def fetch(self, body):
        page_body = etree.HTML(body)
        res = []
        assert 'title' in self._parse_rule, 'wrong in title'
        assert 'url' in self._parse_rule, 'wrong in url'
        urls = page_body.xpath(self._parse_rule['url'])
        titles = page_body.xpath(self._parse_rule['title'])
        date_time = '{:%m-%d}'.format(datetime.datetime.today())
        for i, date in enumerate(page_body.xpath(self._parse_rule['pub_date'])):
            if date == date_time:
                u = urls[i]
                t = titles[i].replace('\r\n', '').replace(' ', '')
                res.append([t, u])
            # res.append(','.join([title.text, page_body.xpath(self._parse_rule['url'])[i]]))
        return res


class QCWYDownloadComment(XpathCrawler):
    def __init__(self, *args, **kwargs):
        super(QCWYDownloadComment, self).__init__(*args, **kwargs)
        self._file_num = 0

    def fetch(self, body):
        page_body = etree.HTML(body)
        res = {}
        for k, v in self._parse_rule.items():
            try:
                if k is 'content':  # 处理一下字符串
                    res[k] = ''.join(page_body.xpath(v)) \
                        .replace('\n', '').replace('\t', '').replace('\r', '')
                else:
                    res[k] = page_body.xpath(v)[0].replace('\t', '')
            except IndexError:  # 抛出剥取异常
                res[k] = 'wrong context xpath'
            except XPathError:  # 为什么这个异常没有捕捉到
                res[k] = 'other wrong xpath'
        return res

    def store(self, res):
        date_time = '{:%Y-%m-%d}'.format(datetime.datetime.today())
        folder_name = './' + date_time
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        with open(folder_name + '/q' + str(self._file_num), 'wb') as wf:
            pickle.dump(res, wf)
        self._file_num += 1


@time_clock
def run_crawler(crawler, url, parse_rule, *args, **kwargs):
    loop = asyncio.get_event_loop()
    dd = crawler(url, parse_rule, loop=loop, *args, **kwargs)
    loop.run_until_complete(dd.crawl())
    dd.close()


@time_clock
def zhilian():
    url = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E7%8F%A0%E6%B5%B7&kw=python&sm=0&p=1&isfilter=0&fl=766&isadv=0&sb=2'
    run_crawler(ZHILIANDownloadUrl, url, ZHILIAN_INFO_RULE, name='zhilian')

    urls = []
    with open('./zhilian', 'rb') as rf:
        ll = pickle.load(rf)
        for l in ll[:20]:
            urls.append(l[-1])

    run_crawler(ZHILIANDownloadComment, urls, ZHILIAN_DETAIL_RULE)


@time_clock
def qianchengwuyou():
    url = 'http://search.51job.com/list/030500,000000,0000,00,9,99,python,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=1&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    run_crawler(QCWYDownloadURL, url, QIANCHENGWUYOU_INFO_RULE, name='qianchengwuyou')

    urls = []
    with open('./qianchengwuyou', 'rb') as rf:
        ll = pickle.load(rf)
        for l in ll:
            urls.append(l[-1])

    run_crawler(QCWYDownloadComment, urls, QIANCHENGWUYOU_DETAIL_RULE)


if __name__ == '__main__':
    # zhilian()
    # qianchengwuyou()
    run_crawler(QCWYDownloadURL, 'http://www.google.com', {})
