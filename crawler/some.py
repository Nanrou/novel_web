import pickle
import os
import time
from collections import Counter

import requests
from bs4 import BeautifulSoup


def somesome():
    cc = ['xuanhuan', 'dushi', 'junshi', 'lishi', 'wuxia', 'xianxia']
    dd = {}
    ll = set()
    try:
        for c in cc:
            resp = requests.get('http://www.22ff.com/{}'.format(c))
            body = resp.content.decode('gbk').encode('utf-8').decode('utf-8')
            soup = BeautifulSoup(body, 'lxml')
            for li in soup.find_all('li', class_='neirong1'):
                # dd[li.string] = 'http://www.22ff.com/{}'.format(li.a['href'])
                ll.add(('http://www.22ff.com{}'.format(li.a['href']), li.string))
            print('done', c)
            time.sleep(0.3)
    except:
        pass
    # with open('all_url.pickle', 'wb') as wf:
    #     pickle.dump(dd, wf)
    with open('all_urls.txt', 'w') as wf:
        wf.write('\n'.join([','.join(l) for l in ll]))


def count_cate():
    files = os.listdir('./tmp')
    res = []
    for file in files:
        with open(os.path.join('./tmp', file), 'rb') as rf:
            pp = pickle.load(rf)
        res.append(pp['category'])
    cc = Counter(tuple(res))
    print(cc.most_common())


if __name__ == '__main__':
    count_cate()
