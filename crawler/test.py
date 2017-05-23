# -*- coding:utf-8 -*-


import aiohttp
import asyncio
import pickle
import random
import re


URL = 'http://www.ranwen.org/files/article/56/56048/10973525.html'
# URL = 'http://www.ranwen.org/files/article/56/56048/'

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as resp:
            page = await resp.text()
            page = etree.HTML(page)
            content = page.xpath('//div[@class="bookname"]/h1')
            # content = page.xpath('//div[@class="box_con"]/div[@id="list"]/dl/dd/a/@href')
            print(type(content))
            print(len(content))
            for c in content:
                # print(etree.tounicode(c))
                print(c)


async def sf():
    ll = []
    i = 0
    while True:
        asyncio.sleep(random.randint(1, 5))
        print('i am %s' % i)
        ll.append(i)
        i += 1
        if i > 20:
            break
    return ll


def gf(p, e):
    while True:
        e.wait()
        print('get {}'.format(p.recv()))
        if p.recv() == -1:
            break
        e.clear()


def producte_cate():
    category = ['玄幻修仙', '科幻网游', '都市重生', '架空历史', '恐怖言情', '全本小说']
    cate = ['xuanhuan', 'kehuan', 'dushi', 'jiakong', 'kongbu', 'quanben']
    res = []
    for i in range(len(cate)):
        res.append({'id': i+1, 'category': category[i], 'cate': cate[i]})
    return res


class Parent(object):
    def __init__(self, a):
        self.a = a

    async def run(self, b):
        self.a += b
        print(self.a)

    async def work(self):
        asyncio.sleep(2)
        await self.run(2)


def split_txt(txt_path, title_rule=None, stone_path='./', chapter_index=None):


    """
    t_rule = r'第一篇'
    t_path = 'test/xue.txt'
    split_txt(t_path, title_rule=t_rule, stone_path='./book/01')

    :param txt_path:
    :param title_rule:
    :param stone_path:
    :param chapter_index:
    :return:
    """
    if not stone_path.endswith('/'):
        stone_path += '/'
    assert isinstance(chapter_index, int) is True, 'require index'
    chapter_index = chapter_index * 10000 + 1

    with codecs.open(txt_path, 'r', encoding='utf-8') as f:
        ls = f.readlines()
        start_index = None
        for index, line in enumerate(ls):
            if re.match(title_rule, line):

                    if start_index is None:
                        start_index = index
                        tmp_ll = line.strip().split(' ')
                        if len(tmp_ll) == 4:
                            chapter_title = ' '.join(tmp_ll[-2:])
                        elif len(tmp_ll) == 5:
                            chapter_title = ' '.join(tmp_ll[-3:])
                        else:
                            chapter_title = ' '.join(tmp_ll[-4:])
                        continue  # 跳过第一次

                    end_index = index
                    res = {
                        'id': chapter_index,
                        'title': '雪鹰领主',
                        'chapter': chapter_title,
                        'content': ''.join(ls[start_index + 1:end_index-2]).replace('\r\n\r\n', '<br/>').replace('  ', '　'),
                        # 'content': ''.join(ls[start_index + 1:end_index-2]),
                    }
                    with open(stone_path + str(chapter_index), 'wb') as wf:
                        pickle.dump(res, wf)
                    chapter_index += 1
                    start_index = end_index
                    tmp_ll = line.strip().split(' ')
                    if len(tmp_ll) == 4:
                        chapter_title = ' '.join(tmp_ll[-2:])
                    elif len(tmp_ll) == 5:
                        chapter_title = ' '.join(tmp_ll[-3:])
                    else:
                        chapter_title = ' '.join(tmp_ll[-4:])

        else:
            res = {
                'id': chapter_index,
                'title': '雪鹰领主',
                'chapter': chapter_title,
                'content': ''.join(ls[start_index + 1:end_index-2]).replace('\r\n\r\n', '<br/>').replace('  ', '　'),
                # 'content': ''.join(ls[start_index + 1:end_index-2]),
            }
            with open(stone_path + str(chapter_index), 'wb') as wf:
                pickle.dump(res, wf)


from lxml import etree
import codecs
import time

if __name__ == '__main__':
    from my_crawler import search_novel

    SEARCH_URL = 'http://www.ranwenw.com/modules/article/search.php'
    download_url = {}
    with codecs.open('titles_list.txt', 'r', encoding='utf-8') as rf:
        for index, title in enumerate(rf.readlines()):

            title = title.strip()
            url = search_novel(index+1, title, url=SEARCH_URL, stone_path='./info/')
            if url:
                print('done {}'.format(title))
            else:
                url = ''
                print('not found {}'.format(title))
            time.sleep(12)

            with codecs.open('download_url', 'a', encoding='utf-8') as wf:
                wf.write(title + ',' + url)



