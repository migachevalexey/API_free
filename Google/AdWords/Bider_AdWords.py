import pprint

from googleads import adwords

'''
Программа обновляет ставки в AdWords по заданному агоритму(пока не разрработан).
За основу берем 'CpcBid' - текущая ставка, 'FirstPositionCpc', 'TopOfPageCpc', 'FirstPageCpc'
В зависисмости от соотношения этих показателей - назначаем ставку, что бы не дорого, но в тоже время быть наверху.
В идеале -  прикрутить сюда статистику по показам и кликам, что бы на ходовые ключи назначать с мультипликатором! 
По умолчанию работает только с кампаниями\группами\слованим в статусе Enabled. 
Можно задавать исключения для кампаний:
    'field': 'CampaignName',
    'operator': 'NOT_IN',
    'values': ['KMC_Stol','Brend']
'''

version_lib = 'v201802'
PAGE_SIZE = 500
adwords_client = adwords.AdWordsClient.LoadFromStorage('C:\Python\googleads.yml')
# adwords_client = adwords.AdWordsClient.LoadFromStorage() по умолчанию
# что бы каждый раз не писать вызов, делаем список и потом работаем с его элементами
val_service = [adwords_client.GetService(i, version=version_lib) for i in ['CampaignService', 'AdGroupService', 'AdGroupCriterionService']]


def campaing_list(client):

    ''' Получаем список ID кампаний(CampaignStatus = ENABLED), по заданному AdWords ClienID (xxx-xxx-xxxx)
    AdWords ClienID берется из googleads.yaml, но можно и указать вручную,
    См. вызов main '''

    # Construct selector and get all campaigns.
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': "ENABLED"
            },
            {
                'field': 'CampaignName',
                'operator': 'IN',
                'values': ['Brand']
                #'values': ['Brand','Brand_Pure_South','Dynamic_Ads','PLA']
            },
        ]}
    page = val_service[0].get( selector)  # val_service - моя переменная-список, см начало скрипта
    if 'entries' in page:
        return [campaign['id'] for campaign in page['entries']]
    else:
        print('No campaigns were found.')


def AdGroup_list(client):
    "Получаем список групп по кампаниям, которые получили из campaing_list"
    campaign_id = campaing_list(client)
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'IN',
                'values': campaign_id
            },
            {
                'field': 'AdGroupStatus',
                'operator': 'EQUALS',
                'values': "ENABLED"}
        ],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    more_pages = True
    AdG_list = []
    while more_pages:
        page = val_service[1].get(selector)
        if 'entries' in page:
            AdG_list += [ad_group['id'] for ad_group in page['entries']]
        else:
            print('No ad groups were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

    return AdG_list


def keywords(client):
    adgroup_id = AdGroup_list(client)
    offset = 0
    selector = {
        'fields': ['Id', 'CriteriaType', 'KeywordText', 'CpcBid', 'FirstPositionCpc', 'TopOfPageCpc', 'FirstPageCpc',
                   'Status'],
        'predicates': [
            {
                'field': 'AdGroupId',
                'operator': 'IN',
                'values': adgroup_id
            },
            {
                'field': 'CriteriaType',
                'operator': 'EQUALS',
                'values': ['KEYWORD']
            },
            {
                'field': 'Status',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            }
        ],

        # 'dateRange':{'min':'20170101', 'max':'20170730'},

        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)},

        'ordering': [{'field': 'AdGroupId', 'sortOrder': 'ASCENDING'}]
    }
    page = val_service[2].get(selector)
    more_pages = True
    d = {}
    while more_pages:
        if 'entries' in page:
            for keyword in page['entries']:
                if keyword['criterionUse'] != 'NEGATIVE':
                    # обрабатываем все варинаты ставок firstPositionCpc,topOfPageCpc != None
                    # topOfPageCpc = None => firstPositionCpc = none
                    # topOfPageCpc != None , но firstPositionCpc = None
                    if (keyword['firstPositionCpc'] is not None and keyword['topOfPageCpc'] is not None):
                        d.setdefault(keyword['adGroupId'], []).append([keyword['criterion']['id'],
                                                                       keyword['biddingStrategyConfiguration']['bids'][0][
                                                                           'bid']['microAmount'],
                                                                       keyword['firstPositionCpc']['amount']['microAmount'],
                                                                       keyword['topOfPageCpc']['amount']['microAmount'],
                                                                       keyword['firstPageCpc']['amount']['microAmount']])
                    elif keyword['topOfPageCpc'] is None:
                        d.setdefault(keyword['adGroupId'], []).append([keyword['criterion']['id'],
                                                                       keyword['biddingStrategyConfiguration']['bids'][0][
                                                                           'bid']['microAmount'],
                                                                       0, 0,
                                                                       keyword['firstPageCpc']['amount']['microAmount']])
                    elif (keyword['topOfPageCpc'] is not None and keyword['firstPositionCpc'] is None):
                        d.setdefault(keyword['adGroupId'], []).append([keyword['criterion']['id'],
                                                                       keyword['biddingStrategyConfiguration']['bids'][0][
                                                                           'bid']['microAmount'],
                                                                       0, keyword['topOfPageCpc']['amount']['microAmount'],
                                                                       keyword['firstPageCpc']['amount']['microAmount']])

        else:
            print(keyword, 'No keywords were found.')

        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

    return d


def bid_update(ad_group_id, key_id, bid_Amount, bid_position):

    operations = [{
        'operator': 'SET',
        'operand': {
            'xsi_type': 'BiddableAdGroupCriterion',
            'adGroupId': ad_group_id,
            'criterion': {
                'id': key_id,
            },
            'biddingStrategyConfiguration': {
                'bids': [
                    {
                        'xsi_type': 'CpcBid',
                        'bid': {
                            'microAmount': bid_Amount
                        }}]}}}]

    val_service[2].mutate(operations)
    print(key_id, int(bid_Amount)/1000000, bid_position)


def main(client):
    for key, it in keywords(client).items():
        for i in it:
            if i[2] == i[1]:
                continue
            elif i[2] > 0 and i[2] != i[1]:
                bid_update(key, i[0], str(i[2]), 'firstPositionCpc')
            elif i[3] != 0:
                bid_update(key, i[0], str(int((i[3]*1.2//10000)*10000)), 'topOfPageCpc')
            elif i[3] == 0:
                bid_update(key, i[0], str(i[4]), 'firstPageCpc')


if __name__ == '__main__':
    # adwords_client.SetClientCustomerId('123-456-7890')
    main(adwords_client)