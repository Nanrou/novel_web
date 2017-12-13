import requests
from bs4 import BeautifulSoup


ll = []
try:
    for i in range(1, 100):
        resp = requests.get('http://superxiaoshuo.com/info/{}'.format(i), timeout=3)
        if resp.status_code == 200:
            print('get ', i)
            soup = BeautifulSoup(resp.text, 'lxml')
            title = soup.find('h1').string
            ll.append(title)
        else:
            break
except:
    pass

print(ll)
with open('./my_title.txt', 'a') as af:
    af.write('\n'.join(ll))
