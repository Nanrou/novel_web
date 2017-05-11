# -*- coding:utf-8 -*-

import requests
from lxml import etree
import codecs
from transfrom import del_extra
import re

MODIFIED_TEXT = [r'一秒记住.*?。', r'(看书.*?)', r'纯文字.*?问', r'热门.*?>', r'最新章节.*?新',
                 r'は防§.*?e', r'&.*?>', r'r.*?>', r'c.*?>',
                 r'复制.*?>', r'字-符.*?>', r'最新最快，无.*?。',
                 r'    .Shumilou.Co  M.Shumilou.Co<br /><br />', r'[Ww]{3}.*[mM]',
                 r'&amp;nbsp;    &amp;nbsp;    &amp;nbsp;    &amp;nbsp;  ']

HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0 '}
URL = 'http://www.xxbiquge.com/5_5422/'


def crawl_urls(u):
    response = requests.get(u, headers=HEADER)
    body = etree.HTML(response.content)
    content_urls = body.xpath('//div[@class="box_con"]/div/dl//dd/a/@href')
    for pk_id, u in enumerate(content_urls):
        content_url = 'http://www.xxbiquge.com' + u
        yield pk_id, content_url


def crwal(content_url):
    """ 爬出目标网站的目标文章，并过滤文章"""
    content_response = requests.get(content_url, headers=HEADER)
    content_body = etree.HTML(content_response.content)
    try:
        chapter = content_body.xpath('//div[@class="bookname"]/h1/text()')[0]
        content = content_body.xpath('//div[@id="content"]')[0]
    except IndexError:
        raise IndexError('rules haved change in %s' % content_url)
    final_content, need_confirm = transform_content(etree.tounicode(content))
    final_content = content_filter(final_content)
    return chapter, final_content, need_confirm


def transform_content(txt):
    need_confirm = 0
    if 'div' in txt:
        txt = txt.split('<div id="content">')[-1].split('</div>')[0]
    if len(txt) > 0:
        while True:
            if txt.startswith(' ') or txt.startswith('　'):
                break
            if '\u4e00' <= txt[0] <= '\u9fff':
                break
            txt = txt[1:]
    txt = del_extra(txt)
    if '\\' in txt or len(txt) < 100:
        need_confirm = 1
    return txt, need_confirm


def content_filter(content):
    """ 正则去除文章中间的广告，乱码"""
    m_content = content
    for ccc in MODIFIED_TEXT:
        m_content = re.sub(ccc, '', m_content)
    return m_content

if __name__ == '__main__':
    # crwal(URL)
    # with codecs.open('test.html', 'r', encoding='utf-8') as f:
    #     body = etree.HTML(f.read())
    #     content = body.xpath('//div[@id="content"]')[0]
    #     print(type(content))
    #     print(etree.tounicode(content).split('<div id="content">')[-1].split('</div>')[0])

    from orm import insert
    import time
    from random import randint
    import redis
    conn = redis.Redis()
    # urls = crawl_urls(URL)
    i = 1171
    # for _, u in urls:
    #     conn.lpush('url', u)
    # for pk_id, url in urls:
    while True:
        url = conn.rpop('url')
        if not url:
            break
        time.sleep(randint(1, 3))
        pk_id = i
        c, t, n = crwal(url)
        insert(pk_id=str(pk_id), chapter=c, content=t, need_confirm=n)
        print('finish: {}'.format(url) + '\n')
        i += 1

