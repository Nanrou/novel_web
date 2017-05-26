# -*- coding:utf-8 -*-
"""
5.20
降耦合，把功能重新细分出来

5.22
listdir 的顺序是随机的，所以要order

"""
import os
import sys
import time
from functools import wraps
import asyncio
import collections

# sys.path.append('./')
import redis

from my_crawler import InfoCrawler, DetailCrawler, run_crawler
from operateDB import insert_to_detail, insert_to_info
from my_logger import MyLogger
from my_decorate import time_clock


Logger = MyLogger('main')


DETAIL_RULE = {
    'title': '//div[@class="con_top"]/a[3]/text()',
    'chapter': '//div[@class="bookname"]/h1/text()',
    'content': ['//div[@id="content"]', ],
    }
# DETAIL_URLS = [[0, 'http://www.ranwen.org/files/article/56/56048/10973525.html'],
#                [1, 'http://www.ranwen.org/files/article/56/56048/11281440.html'], ]

# INFO_URLS = 'http://www.ranwen.org/files/article/19/19388/'
INFO_RULE = {
    'urls': '//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href',
    'title': '//div[@id="maininfo"]/div[@id="info"]/h1/text()',
    'author': '//div[@id="maininfo"]/div[@id="info"]/p[1]/text()',
    'status': '//div[@id="maininfo"]/div[@id="info"]/p[2]/text()',
    'category': '//div[@class="con_top"]/a[2]/text()',
    'resume': '//div[@id="maininfo"]/div[@id="intro"]/p[1]/text()',
    'img_url': '//div[@id="fmimg"]/img/@src',
    }


def download_info(info_urls):
    # loop = asyncio.get_event_loop()
    # asyncio.set_event_loop(None)
    # infoc = InfoCrawler(urls=info_urls, parse_rule=INFO_RULE, loop=loop, store_path='./info')
    # loop.run_until_complete(infoc.crawl())
    # infoc.close()
    # loop.close()

    infoc = InfoCrawler(urls=info_urls, parse_rule=INFO_RULE, store_path='./info')
    run_crawler(infoc)
    return infoc.store_path


def download_detail(detail_urls):
    detailc = DetailCrawler(urls=detail_urls, parse_rule=DETAIL_RULE, store_path='./book')
    run_crawler(detailc)
    return detailc.store_path



if __name__ == '__main__':
    info_urls = [
        'http://www.ranwen.org/files/article/19/19388/',
        'http://www.ranwen.org/files/article/76/76945/',
        'http://www.ranwen.org/files/article/77/77081/',
        # 'http://www.ranwen.org/files/article/56/56048/',
                 ]

    # download_info(info_urls)
    # t = threading.Thread(target=get_url_from_redis, args=['1'])  # 怎么在线程中调用事件循环好呢
    # t.setDaemon(True)
    # t.start()
    # t.join()

    # insert_detail('book/chapter/02')
    # insert_info('./info/')
    # for i in range(21, 29):
    #     s = 'book/chapter/{i:0>2}'.format(i=i)
    #     insert_detail(s)
