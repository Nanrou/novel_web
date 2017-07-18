# -*- coding:utf-8 -*-

import sys
import os
import codecs
import asyncio
import datetime
import pickle
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath('__file__')))))


import requests
from lxml import etree
from lxml.etree import XPathError

from crawler.crawler.my_crawler import XpathCrawler
from crawler.crawler.my_exception import FetchError
from crawler.utls.my_logger import MyLogger
from crawler.utls.my_decorate import time_clock

LOGGER = MyLogger('zhiye')

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN'
}

ZHILIAN_INFO_RULE = {
    'title': '//table[@class="newlist"]/tr/td[@class="zwmc"]/div/a',
    'url': '//table[@class="newlist"]/tr/td[@class="zwmc"]/div/a/@href'
}

ZHILIAN_DETAIL_RULE = {
    'title': '//div[@class="fixed-inner-box"]/div/h1/text()',
    'company': '//div[@class="fixed-inner-box"]/div/h2/a/text()',
    'salary': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[1]/strong/text()',
    'work_des': '//div[@class="terminalpage-left"]/ul[@class="terminal-ul clearfix"]/li[2]/strong/a/text()',
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
    'content': '//div[@class="bmsg job_msg inbox"]',
}

LAGOU_DATA = ('user_trace_token', 'SEARCH_ID', 'JSESSIONID')

LAGOU_DETAIL_RULE = {
    'title': '//span[@class="name"]/text()',
    'company': '//div[@class="company"]/text()',
    'salary': '//span[@class="salary"]/text()',
    'work_des': '//div[@class="work_addr"]/text()',
    'content': '//dd[@class="job_bt"]/div',
}


def download_html(url):
    """
    下载html页面，做测试用
    :param url:
    :return:
    """
    response = requests.get(url, headers=HEADERS)
    content = response.content.decode(response.apparent_encoding).encode('utf-8').decode('utf-8')
    try:
        with open('hhh.html', 'w') as wf:
            wf.write(content)
    except UnicodeError:
        with codecs.open('hhh.html', 'w', encoding='utf-8') as wf:
            wf.write(content)


class ZHILIANDownloadUrl(XpathCrawler):
    """
    爬取子页面的url
    """
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
        self._prefix = 'z'

    def fetch(self, body):
        """
        抓取的逻辑，负责报异常
        :param body:
        :return:
        """
        page_body = etree.HTML(body)
        res = {}
        wrong_times = 0
        for k, v in self._parse_rule.items():
            try:
                res.update(self.fetch_detail(page_body, k, v))
            except IndexError:  # 抛出剥取异常
                res[k] = 'miss {}'.format(k)
                wrong_times += 1
            except XPathError:
                res[k] = 'other wrong xpath'
        if wrong_times > 3:
            raise FetchError('{} items miss, so retry again'.format(wrong_times))
        return res

    def fetch_detail(self, page_body, k, v):
        """
        处理字符串的具体操作
        :param page_body:
        :param k:
        :param v:
        :return:
        """
        res = {}
        if k is 'content':
            res[k] = page_body.xpath(v)[0].xpath('string(.)') \
                .replace('\r\n', '').replace('\xa0', '').replace(' ', '')
        else:
            res[k] = page_body.xpath(v)[0].replace('\xa0', '')
        return res

    def store(self, res):
        date_time = '{:%Y-%m-%d}'.format(datetime.datetime.today())
        folder_name = './' + date_time
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        # with open(folder_name + '/' + res.get('title'), 'wb') as wf:
        #     pickle.dump(res, wf)
        with open(folder_name + '/' + self._prefix + str(self._file_num), 'wb') as wf:
            pickle.dump(res, wf)
        self._file_num += 1


class QCWYDownloadURL(XpathCrawler):
    """
    爬取子页面的url
    """
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
                _u = urls[i]
                _t = titles[i].replace('\r\n', '').replace(' ', '')
                res.append([_t, _u])
            # res.append(','.join([title.text, page_body.xpath(self._parse_rule['url'])[i]]))
        return res


class QCWYDownloadComment(ZHILIANDownloadComment):
    def __init__(self, *args, **kwargs):
        super(QCWYDownloadComment, self).__init__(*args, **kwargs)
        self._prefix = 'q'

    def fetch_detail(self, page_body, k, v):
        res = {}
        if k is 'content':  # 处理一下字符串
            res[k] = page_body.xpath(v)[0].xpath('string(.)') \
                .replace('\n', '').replace('\t', '').replace('\r', '').replace('\xa0', '')
        else:
            res[k] = page_body.xpath(v)[0].replace('\t', '')
        return res


class LAGOUDownloadComment(ZHILIANDownloadComment):
    def __init__(self, *args, **kwargs):
        super(LAGOUDownloadComment, self).__init__(*args, **kwargs)
        self._prefix = 'l'

    # def fetch(self, body):
    #     page_body = etree.HTML(body)
    #     res = {}
    #     for k, v in self._parse_rule.items():
    #         try:
    #             if k is 'content':
    #                 res[k] = page_body.xpath(v)[0].xpath('string(.)') \
    #                     .replace('\n', '').replace(' ', '').replace('\xa0', '')
    #             elif k is 'work_des':
    #                 res[k] = ''.join(page_body.xpath(v)) \
    #                     .replace('\n', '').replace('-', '').replace(' ', '')
    #             else:
    #                 res[k] = page_body.xpath(v)[0]
    #         except IndexError:  # 抛出剥取异常
    #             raise FetchError(v)
    #         except XPathError:
    #             res[k] = 'wrong xpath syntax'
    #     return res

    def fetch_detail(self, page_body, k, v):
        res = {}
        if k is 'content':
            res[k] = page_body.xpath(v)[0].xpath('string(.)') \
                .replace('\n', '').replace(' ', '').replace('\xa0', '')
        elif k is 'work_des':
            res[k] = ''.join(page_body.xpath(v)) \
                .replace('\n', '').replace('-', '').replace(' ', '')
        else:
            res[k] = page_body.xpath(v)[0]
        return res


def run_phantomjs_to_get_cookies(url=None, js_script='lagou.js'):
    if url is None:
        url = 'https://www.lagou.com/jobs/list_Python?px=default%26 city=%E7%8F%A0%E6%B5%B7#order'
    cmd = 'phantomjs' + ' ' + js_script + ' ' + url
    os.system(cmd)


def get_lagou_headers(filename='lagou_cookies.txt'):
    _header = {
        'Host': 'www.lagou.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:54.0) Gecko/20100101 Firefox/54.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Anit-Forge-Token': 'None',
        'X-Anit-Forge-Code': '0',
        'Referer': 'https://www.lagou.com/jobs/list_Python?px=default&city=%E7%8F%A0%E6%B5%B7',
        'Content-Length': '25',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    res = {}
    with open(filename, 'r') as rf:
        for line in rf.readlines():
            k, v = line.strip().split('=')
            # if k in LAGOU_DATA:
            res[k] = v
            # continue

    _header.update(res)
    return _header


def get_lagou_info():
    ajax_url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city=珠海&needAddtionalResult=false'
    _data = {
        'first': 'true',
        'pn': '1',
        'kd': 'Python',
    }
    _header = get_lagou_headers()
    _session = requests.session()
    resp = _session.post(ajax_url, _data, headers=_header)
    with open('lagou_info.json', 'w') as wf:
        wf.write(resp.text)
    _session.close()


class BTestLAGOU(LAGOUDownloadComment):
    """
    爬取拉钩的时候，触发了反爬虫，一部分网址访问不到，这个类作为测试用
    """
    def fetch(self, body):
        return body

    def store(self, res):
        date_time = '{:%Y-%m-%d}'.format(datetime.datetime.today())
        folder_name = './' + date_time
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        try:
            with open(self._prefix + str(self._file_num) + '.html', 'w') as wf:
                wf.write(res)
        except UnicodeError:
            with codecs.open(self._prefix + str(self._file_num) + '.html', 'w', encoding='utf-8') as wf:
                wf.write(res)
        self._file_num += 1


def get_lagou_content(filename='lagou_info.json'):
    with open(filename) as rf:
        info_lists = json.load(rf)
    info_lists = info_lists['content']['hrInfoMap'].keys()
    urls = []
    for info_id in info_lists:
        urls.append('https://www.lagou.com/jobs/{}.html'.format(info_id))
    run_crawler(LAGOUDownloadComment, urls, LAGOU_DETAIL_RULE, name='lagou', waiting_time=5)
    # header = get_lagou_headers()
    # run_crawler(BTestLAGOU, urls, LAGOU_DETAIL_RULE, name='lagou', waiting_time=3)


@time_clock
def lagou():
    """
    先通过phatomjs拿到cookies，然后用这个cookies去构造post拿到工作的id
    然后用这个id去构造url，再爬细节
    :return:
    """
    run_phantomjs_to_get_cookies()
    get_lagou_info()
    get_lagou_content()


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


@time_clock
def collect_detail(folder='./', namelist=('z', 'q', 'l')):
    """
    收集文件夹中的信息，都存到一个文件中，并把其他的都删掉
    :param folder: 指定文件夹的位置
    :param namelist:
    :return:
    """
    for s in namelist:
        res = []
        z_file_names = [i for i in os.listdir(folder) if i.startswith(s)]
        for name in z_file_names:
            file_name = os.path.join(folder, name)
            with open(file_name, 'rb') as rf:
                try:
                    content = pickle.load(rf)
                except EOFError as e:
                    print('{} in {}'.format(e, name))
                    continue
                res.append(content)
                
            os.remove(file_name)
        with open(os.path.join(folder, '{}_sum'.format(s)), 'wb') as wf:
            pickle.dump(res, wf)
            
        res_txt = []
        for i in res:
            res_txt.append(','.join([i['title'], i['company'],
                                    i['salary'], i['work_des'], i['content']]))
        
        with open(os.path.join(folder, '{}_sum.txt'.format(s)), 'w') as wf:
            wf.write('\n'.join(res_txt))


@time_clock
def main():
    date_time = '{:%Y-%m-%d}'.format(datetime.datetime.today())
    if not os.path.exists(date_time):
        zhilian()
        qianchengwuyou()
        lagou()
        collect_detail(date_time)
    else:
        print('today already do it')

    remove_list = ['lagou_cookies.txt', 'lagou_info.json', 'qianchengwuyou', 'zhilian']
    for i in remove_list:
        if os.path.exists(i):
            os.remove(i)

if __name__ == '__main__':
    print('i in zhiye')
    main()
