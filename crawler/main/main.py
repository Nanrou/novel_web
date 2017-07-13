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

from crawler.utls.my_logger import MyLogger
from crawler.crawler.my_crawler import my_search

Logger = MyLogger('main_loop')


DETAIL_RULE = {
    'title': '//div[@class="con_top"]/a[3]/text()',
    'chapter': '//div[@class="bookname"]/h1/text()',
    'content': ['//div[@id="content"]', ],
    }

INFO_RULE = {
    'title': '//div[@class="tname"]/a/text()',
    'author': '//table[@class="fw"]/tbody/tr/td[@class="tc"][1]/a/text()',
    # 'status': ,
    'category': '//table[@class="fw"]/tbody/tr/td[@class="tc"][2]/a/text()',
    'resume': '//span[@itemprop="description"]/text()',
    'img_url': '//img[@class="novel_cover"]/@src',
    'novel_url': '////table[@class="fw"]/tbody/tr[3]/a[last()]/text()',
    }

SEARCH_RULE = {
    'title': '//li[@class="neirong1"]/a/text()',
    'info_url': '//li[@class="neirong1"]/a/@href',
}

FILE = '魔天记'
URL = 'http://www.22ff.com/s_' + FILE
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

    my_search(FILE, URL, SEARCH_RULE)  # 找到小说，拿到info_url

