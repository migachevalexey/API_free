from google.cloud import bigquery
import time

client = bigquery.Client(project='glowing-cargo-144610')

dataset = client.dataset('Axiom')

datasets = client.list_datasets()
# for i in datasets:
    # print(i.name)
# print(dataset, type(dataset) , dataset.etag, dataset.description, dataset.name, dataset.dataset_id, dataset.location)
# d=dataset.list_tables()

for rows in dataset.list_tables():
     if  'streaming_2016' in rows.name: #rows.name.startswith('2016') or rows.name.startswith('streaming_2016'):
        print(rows.name)
        client._connection.api_request(method='DELETE', path=f'/projects/glowing-cargo-144610/datasets/{dataset.name}/tables/{rows.name}')
        time.sleep(0.5)


       

# QUERY = (
#     'select orders_sell_id, money_received, date_time, Site, phone  from [glowing-cargo-144610.Mydata.Borb_Orders]')
# query = client.run_sync_query('{} LIMIT 1000'.format(QUERY))
# query.timeout_ms = 10000
# query.max_results = 10000
# query.run()
# #rows = query.fetch_data(max_results=100) либо так. Тогда в цикле in rows
#
# # for row in query.rows:
# #      print(row)
