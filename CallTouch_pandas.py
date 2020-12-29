import pprint

import requests
import json
import pandas as pd
import re
import matplotlib.pyplot as plt

token = ['111', '123']
site_id = ['4039', '4055']

server_antwort=[]
for  i in range(len(site_id)):
    url = 'https://api-node1.calltouch.ru/calls-service/RestAPI/{}/calls-diary/calls'.format(site_id[i])
    params = {'clientApiId': token[0], 'dateFrom': '01/01/2017', 'dateTo': '13/08/2017', 'page': 1, 'limit': 1000}
    r = requests.get(url, params={'clientApiId': token[i], 'dateFrom': '01/01/2017', 'dateTo': '13/08/2017', 'page': 1,
                              'limit': 1000})
    server_antwort += json.loads(r.text)['records']


a = {}
for k in [i['utmContent'] for i in server_antwort if i['utmContent'] not in ['<не заполнено>', '<не указано>']]:
    if re.search(r'\.1t[1234]', k):
        z = re.sub(r'[0-9]{11}\.1t[1234]', 'premium.' + k[-1], k)
    elif re.search(r'\.1o[1-9]$', k):
        z = re.sub(r'[0-9]{11}\.1o[1-9]$', 'other.' + k[-1], k)
    else:  z = k

    z = re.sub(r'[0-9]{10}\.|BS[1-4]|desktop\.|tablet\.|mobile\.', '', z)
    a[z] = a.get(z, 0) + 1


c = []
# готовим данные для pandas
for i, j in a.items():
    if 'premium' in i or 'other' in i:
        c.append({'name': i, 'count': j})


data = pd.DataFrame(c)
data.set_index('name', inplace=True)
print(data.sort_values(by='count', ascending=False))
data.plot.pie(y='count', title=f'высч', shadow=True, autopct='%1.1f%%',
              explode=tuple([0 if i != 1 else 0.1 for i in range(len(data))]), legend=False)
plt.show()
