from google.cloud import bigquery
import MySQLdb
import json
import datetime
from calendar import monthrange

#Скрипт вытягивает ассоциированные транзакции по всем dataset в BigQuery и insert их в MySQL в таблицу orders_traffic.
#Cкрипт надо запускать в первых числах месяца(3-5число) и он выводит данные за предыдущий месяц


def sql_db_insert(list_tuple_val):
    with open('C:/users/934/PycharmProjects/key/MySQL_db_connect.json') as f:
        param_сonnect = json.load(f)
    db_connect = MySQLdb.connect(user=param_сonnect['user'], passwd=param_сonnect['passwd'],
                                 host=param_сonnect['host'], db=param_сonnect['db'],
                                 charset='cp1251')
    cursor = db_connect.cursor()
    sql_query = r'INSERT INTO orders_traffic (site,orders_sell_id,items_price_sum,sell_datetime,' \
                'source,campaign,keyword,device,bq_status,payment_status,canceled,load_source,comment,customer_id,pro_finished) ' \
                'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    cursor.executemany(sql_query, list_tuple_val)
    db_connect.commit()
    cursor.close()
    db_connect.close()


def connect_BigQuery():
    client = bigquery.Client(project='glowing-cargo-144610')
    datasets = client.list_datasets()
    list_name_dataset = [rows.name for rows in datasets if rows.name not in ['MKrf','Mydata','Axiom','Attribution_Funnel_Based','Temp','YamRussia']]

    return client, list_name_dataset

def last_month():
    curr_date = datetime.date.today()
    month = curr_date.replace(month=datetime.date.today().month - 1)  # предыдущий месяц
    last_day = str(monthrange(curr_date.year, curr_date.month - 1)[1])  # последний день предыдущего месяца
    start_month = month.strftime("%m01")  # в SQL запрос начало предыдущего месяца
    end_month = month.strftime("%m") + str(last_day)  # в SQL запрос конец предыдущего месяца
    table_sufix = curr_date.replace(month=datetime.date.today().month - 2).strftime("%m25")

    return start_month, end_month, table_sufix


def query_shakespeare():
    result = []
    start_month, end_month, table_sufix = last_month()
    print(start_month, end_month)
    client, list_name_dataset = connect_BigQuery()
    with open('AsTransaction.txt', encoding='utf-8') as f:
        SQL_Query = f.read()
    for name_dataset in list_name_dataset:
        query_results = client.run_sync_query(SQL_Query.format(name_dataset, start_month, table_sufix, end_month))
        query_results.timeout_ms = 30000
        query_results.use_legacy_sql = False
        query_results.run()
        rows = query_results.fetch_data(max_results=100)
        if rows:
            result += rows
    print(len(result), result)

    sql_db_insert(result)
    print('Готово')


if __name__ == '__main__':
    query_shakespeare()
