# -*- coding:utf-8 -*-

import os

import redis


from crawler.my_crawler import InfoCrawler, DetailCrawler, run_crawler
from crawler.operateDB import insert_to_detail, insert_to_info
from crawler.my_logger import MyLogger

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
    }


def part_one(info_urls):
    infoc = InfoCrawler(urls=info_urls, parse_rule=INFO_RULE, store_path='./info')
    run_crawler(infoc)

    info_list = os.listdir(infoc.store_path)
    for info in info_list:
        insert_to_info(infoc.store_path + info)


def part_two(detail_urls):

    detailc = DetailCrawler(urls=detail_urls, parse_rule=DETAIL_RULE, store_path='./book')
    run_crawler(detailc)
    print('end crawler')
    folder_list = os.listdir(detailc.store_path)
    for folder in folder_list:
        folder_path = detailc.store_path + folder
        detail_name_list = os.listdir(folder_path)
        # for detail in detail_list:  # 一个文件夹里可能有1000+的文件，不要逐个存入，要一次存入多个
        #     insert_to_detail(folder_path + detail)
        detail_list = [folder_path + '/' + i for i in detail_name_list]
        insert_to_detail(detail_list)

if __name__ == '__main__':

    info_urls = ['http://www.ranwen.org/files/article/19/19388/']

    # part_one(info_urls)

    conn = redis.StrictRedis()
    items = conn.lrange('1', 0, 10)
    detail_urls = []
    for item in items:
        index, url = str(item).split('!')
        detail_urls.append([index[2:], url[:-1]])
    # print(detail_urls)
    part_two(detail_urls)


