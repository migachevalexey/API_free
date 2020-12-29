import argparse
import httplib2
import os
import sys
import re
import MySQLdb
import datetime
import time
import json

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])

CLIENT_SECRETS = 'C:/users/934/PycharmProjects/key/client_id.json'

FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
                                      scope=[
                                          'https://www.googleapis.com/auth/analytics.readonly',
                                            ],
                                      message=tools.message_if_missing(CLIENT_SECRETS))
def sql_db_insert(list_tuple_val):
    with open('C:/users/934/PycharmProjects/key/MySQL_db_connect.json') as f:
        param_сonnect = json.load(f)
    db_connect = MySQLdb.connect(user=param_сonnect['user'], passwd = param_сonnect['passwd'],
                                 host=param_сonnect['host'], db=param_сonnect['db'],
                                 charset='cp1251')
    cursor = db_connect.cursor()
    sql_query = 'INSERT INTO cost_device (campaign, source, device, date, clicks, cost, CPC, site) ' \
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.executemany(sql_query, list_tuple_val)
    db_connect.commit()
    cursor.close()
    db_connect.close()


def change_campaign_name(campaign_name, group_name, keyword, site):

    if site == 'Region_Medica':
        if re.search('МГ_', group_name):
            campaign_name += '_GlazGolov'
        elif re.search('МС_', group_name):
            campaign_name += '_Stol'
        elif re.search('МН_', group_name):
            campaign_name += '_Nakidka'
        elif re.search('НК_', group_name):
            campaign_name += '_NefritKovr'
        elif re.search('Zero', group_name):
            campaign_name += '_Zero'
        elif re.search('МК_', group_name):
            campaign_name += '_Kreslo'
        elif re.search('Бренд', group_name):
            campaign_name += '_Brend'
        else:
            campaign_name += '_Other'

    elif site == 'yamaguchi' and re.match('.*Other', campaign_name):
        if re.search('МГ_',group_name):
            campaign_name = campaign_name.replace('Other', 'GlazGolov')
        elif re.search('МН_', group_name):
            campaign_name = campaign_name.replace('Other', 'Nakidka')
        elif re.search('НК_', group_name):
            campaign_name = campaign_name.replace('Other','NefritKovr')
        elif re.search('Zero', group_name):
            campaign_name = campaign_name.replace('Other', 'Zero')
        elif re.search('Палки', group_name):
            campaign_name = campaign_name.replace('Other', 'Palki_hodba')
        elif re.search('МдН', group_name):
            campaign_name = campaign_name.replace('Other', 'MasNog')
        elif re.search('Валик', group_name):
            campaign_name = campaign_name.replace('Other', 'Valik')

    elif site in ['yamaguchi', 'us-medica'] and campaign_name == 'MerchantCentre':
        if re.search('кресл', keyword):
            campaign_name += '_Kreslo'
        elif re.search('стол', keyword):
            campaign_name += '_Stol'
        elif re.search('ног', keyword):
            campaign_name += '_MasNog'
        elif re.search('накидк', keyword):
            campaign_name += '_Nakidka'
        elif re.search('голов', keyword):
            campaign_name += '_GlazGolov'
        elif re.search('палки', keyword):
            campaign_name += '_Palki_hodba'
        elif re.search('здоровья', keyword):
            campaign_name += '_Tovary_d_zdorovya'
        elif re.search('красоты', keyword):
            campaign_name += '_Tovary_d_krasoty'
        elif re.search('фитнес', keyword):
            campaign_name += '_Fitnes_oborudovanie'
        elif re.search('кроват', keyword):
            campaign_name += '_Krovat'
        elif re.search('подушк', keyword):
            campaign_name += '_Podushka'
        elif re.search('валик', keyword):
            campaign_name += '_Valik'
        else:
            campaign_name += '_Other'

    return campaign_name

def main(argv):
    flags = parser.parse_args(argv[1:])
    storage = file.Storage('C:/users/934/PycharmProjects/key/credentials.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(FLOW, storage, flags)

    http = credentials.authorize(httplib2.Http())
    analytics = discovery.build('analytics', 'v3', http=http)

    # ВРЕМЕННОЙ Интервал
    startDate = datetime.date.today() - datetime.timedelta(days=18)
    stopDate = datetime.date.today() - datetime.timedelta(days=3)

    def api_query(list_var): # передаем в функцию список из переменных
        api_query = analytics.data().ga().get(
            ids=list_var[0],
            metrics='ga:adClicks,ga:adCost,ga:CPC',
            dimensions=list_var[1],
            filters=list_var[2],
            start_date=str(startDate),
            end_date=str(stopDate),
            max_results=10000
            )
        result = api_query.execute()['rows']  # делаем запрос к Google и вытягиваем данные
        for i in result:
            i.append(list_var[3])
        return result

    ga_ids = ('ga:13057763', 'Region_Medica', 'ga:11746937', 'us-medica', 'ga:11684150', 'yamaguchi')
    ya_dimension = 'ga:campaign,ga:source,ga:adContent,ga:date'
    ga_dimension = 'ga:campaign,ga:source,ga:deviceCategory,ga:date,ga:adGroup,ga:keyword'
    filter = (r'ga:medium==cpc;ga:source=@yandex.;ga:adCost>0', r'ga:medium==cpc;ga:source==google')
    sites = [(ga_ids[0], ya_dimension, filter[0], ga_ids[1]), (ga_ids[2], ya_dimension, filter[0], ga_ids[3]), (ga_ids[4], ya_dimension, filter[0], ga_ids[5]),
             (ga_ids[0], ga_dimension, filter[1], ga_ids[1]), (ga_ids[2], ga_dimension, filter[1], ga_ids[3]), (ga_ids[4], ga_dimension, filter[1], ga_ids[5])]
    result = []

    for i in sites:
        result += api_query(i)  # собственно получаем наш массив даных -). ТУТ ВСЕ И РАБОТАЕТ!!


    for i in result:
        if 'google' in i:
            i[0] = change_campaign_name(i[0], i[4], i[5], i[-1])
            del(i[4:6])
        i[4:7] = list(map(lambda x: float(x), i[4:7]))
        i[-2] = round(i[-2], 2)
        i[3] = f'{i[3][0:4]}-{i[3][4:6]}-{i[3][6:8]}'  # Аналогично - '{}-{}-{}'.format(i[3][0:4], i[3][4:6], i[3][6:8])
        if 'google' not in i:
            i[2] = re.sub('\..*', '', i[2])

    for i in result:
        if not re.match(('desktop$|mobile$|tablet$'), i[2]):
            print(i)

    result = [tuple(i) for i in result]
    #for i in result:
     #   if 'google' in i:
      #      print(i)

    try:
        if len(result) > 0:
            print('Записи найдены. Начинаем вставку')

        sql_db_insert(result)  # отправяем данные в базу -)

        print('В бaзу вставили {} записей. За период с {} по {}'.format(len(result), startDate, stopDate))
        time.sleep(7)

    except:
        print("Ошибка!! данные не были вставлены в базу")
        time.sleep(15)

if __name__ == '__main__':
    main(sys.argv)