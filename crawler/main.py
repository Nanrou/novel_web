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

from bs4 import BeautifulSoup

from crawler.my_crawler import AsyncCrawlerBase, run_crawler, NovelDownload
from crawler.my_exception import FetchError
from utls.my_logger import MyLogger
from utls.my_decorate import time_clock
from db.operateDB import insert_to_book, new_insert_chapters

Logger = MyLogger('main_loop')

BOOK_RULE = {
    'author': '',
    'category': '',
    'update_time': '',
    'resume': '',
}


class Bs4Crawler(AsyncCrawlerBase):
    def fetch(self, body):
        try:
            soup = BeautifulSoup(body, 'lxml')
            _tmp = []
            for td in soup.find_all('td', class_='tc'):
                _tmp.append(str(td.string))  # 要注意bs4的string并不是标准的str，pickle的时候要手动转
            res = {k: v for k, v in zip(['author', 'category', 'update_time'], _tmp)}
            res['name'] = str(soup.find('div', class_='tname').string)
            res['resume'] = '<br/>'.join([s for s in soup.find_all('td', colspan='6')[-1].stripped_strings])
        except:
            raise FetchError()
        return res


class Bs4Crawler2(AsyncCrawlerBase):
    ll = []

    def fetch(self, body):
        try:
            soup = BeautifulSoup(body, 'lxml')
            ss = soup.find('div', class_='down_bar').find('td', colspan='3').string
            ss = ss.replace('"', '').split('(')[-1].split(')')[0].split(', ')
            s1, s2, _ = ss
        except:
            raise FetchError()
        return 'http://67.229.159.202/full/{}/{}.txt'.format(s1, s2)

    def store(self, url, u):
        self.ll.append('{},{}'.format(url, u))
        Logger.info('done {}'.format(u))

    def close(self):
        super().close()
        with open('all_download_url.txt', 'a') as af:
            af.write('\n'.join(self.ll))
            af.write('\n')


def doit():
    ll = []
    with open('all_urls.txt') as f:
        for line in f.readlines():
            url, name = line.split(',')
            ll.append(url)
    return ll


def dothat():
    ll = []
    with open('all_download_url.txt') as f:
        for line in f.readlines():
            url, name = line.split(',')
            ll.append(url)
    return ll


def get_header(tt):
    ss = '''Host: www.22ff.com
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Cookie: UM_distinctid=1604a98aab69-02d5851a4d280a8-49566f-1aeaa0-1604a98aab8209; CNZZDATA1255203146=1961916610-1513078159-%7C1513078159
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Pragma: no-cache
Cache-Control: no-cache
Referer: http://www.22ff.com/
'''
    dd = """Host: 67.229.159.202
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Referer: http://www.22ff.com/xs/222103.txt
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Pragma: no-cache
Cache-Control: no-cache
    """
    _dd = {'ss': ss, 'dd': dd}
    if tt not in ['ss', 'dd']:
        raise RuntimeError
    _header = {}
    for line in _dd[tt].split('\n'):
        if line.strip():
            k, v = line.split(':', 1)
            if k == 'Cookie':
                continue
            _header[k] = v.strip()
    return _header


def insert_all_book():  # 更新书信息到数据库
    files = [os.path.join('./tmp', f) for f in os.listdir('./tmp')]
    insert_to_book(files)


def new_split_book(file):  # 新的切分章节
    with open(file, 'r', encoding='utf-8') as rf:
        txt = list(rf.readlines())
    title = txt[0].strip()
    chapter_title = ''
    one_chapter = []
    for index, row in enumerate(txt[1:]):
        if '\u4e00' <= row[0] <= '\u9fff':
            if chapter_title:
                res = {
                    'title': title,
                    'chapter': chapter_title[:60],
                    'content': '<br/>'.join(one_chapter)
                }
                yield res
            chapter_title = row.strip()
            one_chapter = []  # 一定要记得归零
        else:
            one_chapter.append(row.strip())
    last_res = {
        'title': title,
        'chapter': chapter_title[:60],
        'content': '<br/>'.join(one_chapter)
    }
    yield last_res


def insert_chapter(file):  # 切分及插入
    new_insert_chapters(new_split_book(file))


def get_mapping():  # 拿到文件名与书名对应的关系
    dd = {}
    with open('all_urls.txt', 'r') as rf:
        for line in rf.readlines():
            line = line.strip()
            if line:
                url, title = line.split(',')
                title_id = url.split('/')[-2] + '.txt'
                dd[title_id] = title
    return dd


def doit():
    if os.path.exists('./tmp.log'):
        with open('./tmp.log') as af:
            files = list(af.read().split('\n'))
    else:
        files = os.listdir('./novel/book')

    mapping = get_mapping()
    _all = len(files)
    i = 1
    Logger.info('start: {} need to finish'.format(_all))
    try:
        while files:
            file = files.pop()
            insert_to_book(os.path.join('./tmp', mapping[file]))
            insert_chapter(os.path.join('./novel/book', file))
            Logger.info('done {}/{} ({}/{})'.format(mapping[file], file, i, _all))
            i += 1
    except Exception as e:
        Logger.warning('{} fail in {}/{}'.format(e, mapping[file], file))
        with open('./tmp.log', 'w') as wf:
            wf.write('\n'.join(files))


if __name__ == '__main__':
    # bb = '2017-05-29 00:08'
    # dd = datetime.strptime(bb, '%Y-%m-%d %H:%M')
    # print(datetime.now() - dd > timedelta(60))

    # urls = doit()
    # urls = [''.join([url[:-1], '.txt']) for url in urls]
    # urls = dothat()
    # headers = get_header('dd')
    # run_crawler(NovelDownload, [urls[1]], headers=headers)
    # for index, r in enumerate(new_split_book('./novel/160163.txt')):
    #     print(r)
    #     if index > 20:
    #         break
    # insert_to_book('./tmp/惊悚乐园')
    # insert_chapter('./novel/160163.txt')
    # doit()
    pass
