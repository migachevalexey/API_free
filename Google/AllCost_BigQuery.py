from google.cloud import bigquery
import MySQLdb
import json
'''
    Удаляем расходы из таблици cost MySql и из AllCost BigQuery
    и затягивает туда данные по расходам, взятые из view Mydata.Cost_Data_fix_date.
    Вся эта муть из-за того, что owox запаздывает с данными и в AllCost они не совсем верные(5% недостает).
    AllCost по сути из схемы можно исключить, но пусть будет для истории.
'''

time_interval = ('2017-09-01', '2017-09-01')


def sql_db_job(list_tuple_val):
    with open('C:/users/934/PycharmProjects/key/MySQL_db_connect.json') as f:
        param_сonnect = json.load(f)
    db_connect = MySQLdb.connect(user=param_сonnect['user'], passwd=param_сonnect['passwd'],
                                 host=param_сonnect['host'], db=param_сonnect['db'],
                                 charset='cp1251')
    cursor = db_connect.cursor()
    sql_del = 'DELETE FROM cost WHERE date BETWEEN %s and %s'
    cursor.execute(sql_del, time_interval)
    db_connect.commit()

    sql_insert = 'INSERT INTO cost (site, source, campaign, date, sum, clicks ) ' \
                 'VALUES (%s, %s, %s, %s, %s, %s)'
    cursor.executemany(sql_insert, list_tuple_val)
    db_connect.commit()

    cursor.close()
    db_connect.close()


def stream_data():
    client = bigquery.Client(project='glowing-cargo-144610')
    dataset = client.dataset('Mydata')
    QUERY_sel = (
        'select  Site, Source, Campaign, date, Summa, Kliki  from [glowing-cargo-144610.Mydata.Cost_Data_fix_date] where date BETWEEN "{}" and "{}"'.format(
            time_interval[0], time_interval[1]))
    QUERY_del = (
        'delete from `glowing-cargo-144610.Mydata.AllCost` where date BETWEEN "{}" and "{}"'.format(
            time_interval[0], time_interval[1]))

    q_del = client.run_sync_query('{}'.format(QUERY_del))
    q_sel = client.run_sync_query('{}'.format(QUERY_sel))
    q_del.use_legacy_sql = False
    q_sel.timeout_ms = 100000
    q_sel.max_results = 100000
    q_del.run()
    q_sel.run()
    list_tuple_val = [row for row in q_sel.rows]
    return list_tuple_val, dataset.table('AllCost')


def main():
    data, table = stream_data()
    sql_db_job(data)
    table.reload()
    table.insert_data(data)


if __name__ == '__main__':
    main()
