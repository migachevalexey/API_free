from pprint import pprint
from urllib.parse import urlencode, urljoin
import requests


TOKEN = 'AAA'

r= requests.get('https://api-metrika.yandex.ru/management/v1/clients', headers = {'Authorization': 'OAuth AAAAA'}, params={'counters':9503158}).json()
print(r)

class YMBase:
    MANAGEMENT_URL = 'https://api-metrika.yandex.ru/management/v1/'
    STAT_URL = 'https://api-metrika.yandex.ru/stat/v1/data'

    def get_headers(self):
        return {
            'Authorization': 'OAuth {}'.format(self.token),
            'Content-Type': 'application/x-yametrika+json',
            'User-Agent': 'Chrome'
        }


class YandexMetrika(YMBase):

    def __init__(self, token):
        self.token = token

    def get_counters(self):
        url = urljoin(self.MANAGEMENT_URL, 'counters')
        headers = self.get_headers()
        response = requests.get(url, headers=headers, params={'pretty': 1})
        counters = response.json()['counters']
        return  [Counter(self.token, i['id']) for i in counters] #[ {i['id']: i['name']}  for i in  counters if i['status']=='Active']


class Counter(YMBase):

    def __init__(self, token, counter_id):
        self.token = token
        self.id = counter_id

    def get_visits(self):
        headers = self.get_headers()
        params = {
            'id': self.id,
            'metrics': 'ym:ad:visits'
        }
        response = requests.get(self.STAT_URL, params, headers=headers)
        return response.json()

    @property
    def views(self):
        headers = self.get_headers()
        params = {
            'id': self.id,
            'metrics': 'ym:ad:visits'
            # 'dimensions':'ym:s:deviceCategory'
        }
        response = requests.get(self.STAT_URL, params, headers=headers)
        return response.json()#['data']#[0]['metrics']


ym = Counter(TOKEN,9503158)
print(ym.views)
# for i in  ym.views:
#     print('{}: Показатель отказов - {:.2f}%, глубина просмотра - {:.2f}стр., процент роботов - {:.2f}%'.format(i['dimensions'][0]['name'], *i['metrics']))

# counters = ym.get_counters()
#
# for counter in counters:
#      pprint(counter.get_visits())
#      pprint(counter.views)

