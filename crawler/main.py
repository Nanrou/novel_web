# -*- coding:utf-8 -*-

import os

import redis


from crawler.my_crawler import InfoCrawler, DetailCrawler, run_crawler
from crawler.operateDB import insert_to_detail, insert_to_info


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

url_list = []

infoc = InfoCrawler(urls=url_list, parse_rule=INFO_RULE, store_path='./info')
run_crawler(infoc)
info_list = os.listdir(infoc.store_path)
for info in info_list:
    insert_to_info(infoc.store_path + info)

conn = redis.StrictRedis()  # 将取出的url放到tmp，爬完了再删掉

detail_urls = []
detailc = DetailCrawler(urls=detail_urls, parse_rule=DETAIL_RULE, store_path='./book')
folder_list = os.listdir(detailc.store_path)
for folder in folder_list:
    folder_path = detailc.store_path + folder
    detail_list = os.listdir(folder_path)
    for detail in detail_list:  # 一个文件夹里可能有1000+的文件，不要逐个存入，可以多个存入
        insert_to_detail(folder_path + detail)
