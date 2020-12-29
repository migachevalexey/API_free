import pprint

import requests
import json
import MySQLdb
import random

# Забираем номера телефонов из проекта ЯМ 8-800 Маркет и insert их в google_traffic
# Так же забирает записи звонков и хранит их в папке ./Calltouch_Sound

with open('C:/users/934/PycharmProjects/key/Calltouch_token.txt') as f_token, \
     open('C:/users/934/PycharmProjects/key/MySQL_db_connect.json') as f_db:
    token = f_token.read()
    param_сonnect_db = json.load(f_db)

site_id = '12693'
url = 'https://api-node1.calltouch.ru/calls-service/RestAPI/{}/calls-diary/calls'.format(site_id)
params = {'clientApiId': token, 'dateFrom': '01/07/2017', 'dateTo': '31/07/2017', 'page': 1, 'limit': 1000}
db_connect = MySQLdb.connect(user=param_сonnect_db['user'], passwd=param_сonnect_db['passwd'],
                             host=param_сonnect_db['host'], db=param_сonnect_db['db'])

cursor = db_connect.cursor()


r = requests.get(url, params=params)
server_antwort = json.loads(r.text)['records']

dic=[]
for i in server_antwort:
    i['site'] = 'yamaguchi'
    i['source'] = 'yandex_market'
    i['device'] = random.choice(['tablet', 'mobile', 'desktop'])
    dic.append(tuple([i['callerNumber'], '{}-{}-{}'.format(i['date'][6:10], i['date'][3:5], i['date'][0:2]), i['site'], i['source'], i['device']]))
    url_mp3 = url+'/{}/download'.format(i['callId'])
    r = requests.get(url_mp3, params={'clientApiId': token})
    with open('Calltouch_Sound\{}-{}-{}_{}мин_{}с.mp3'.format(i['callerNumber'][0:4], i['callerNumber'][4:7],i['callerNumber'][7:], i['duration']//60, i['duration']%60), 'wb') as sound_f:
        sound_f.write(r.content)

print(dic)

# for i in server_antwort:
#       print(i['date'], '\t', i['callerNumber'], '\t', '{}мин {}с'.format(i['duration']//60, i['duration'] % 60), '\t', i['source'], i['site'])


cursor.executemany("INSERT INTO google_traffic(phone, call_date, site, source, device) "
                   "VALUES(%s,%s,%s,%s,%s)", list(set(dic)))
db_connect.commit()
cursor.close()
db_connect.close()
