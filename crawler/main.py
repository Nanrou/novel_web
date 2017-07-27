# -*- coding:utf-8 -*-
"""
workflow:
1，生成一个含有很多标题的txt
2，根据这个txt，去搜，并下载info资料，和小说下载的URL  get_novel_urls
3，把info塞到db里  insert_info
4，根据之前的url，去下载整本小说  download_novel
5，将小说分割成章节  product_split_rule --> bbb
6，把detail塞到db里  insert_detail
"""
import os
import sys
import time
import asyncio


from crawler.utls.my_logger import MyLogger
from crawler.crawler.my_crawler import my_search

Logger = MyLogger('main_loop')


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

SEARCH_RULE = {
    'title': '//div[@class="neirong1"]/a/text()',
    'info_url': '//div[@class="neirong2"]/a/@href',
}

FILE = '魔天记'
URL = 'www.22ff.com/s_' + FILE
COOKIE = {
    'UM_distinctid': '15d16bcc49ac5-0e28b2830986c08-395c7818-13c680-15d16bcc49c2d5',
    'CNZZDATA1255203146': '1330539940-1499324798-http%3A%2F%2Fwww.22ff.com%2F|1499324798'
}


if __name__ == '__main__':
    info_urls = [
        'http://www.ranwen.org/files/article/19/19388/',
        'http://www.ranwen.org/files/article/76/76945/',
        'http://www.ranwen.org/files/article/77/77081/',
        # 'http://www.ranwen.org/files/article/56/56048/',
                 ]

    my_search(FILE, URL, SEARCH_RULE)
