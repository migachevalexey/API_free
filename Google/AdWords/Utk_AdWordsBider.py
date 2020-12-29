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
    'operator': 'NOT_IN', # https://developers.google.com/adwords/api/docs/reference/v201710/CampaignCriterionService.Predicate.Operator
    'values': ['KMC_Stol','Brend']
'''

version_lib = 'v201802'
PAGE_SIZE = 10000
# adwords_client = adwords.AdWordsClient.LoadFromStorage() по умолчанию
adwords_client = adwords.AdWordsClient.LoadFromStorage('C:\Python\googleads.yml')
# что бы каждый раз не писать вызов, делаем список и потом работаем с его элементами
val_service = [adwords_client.GetService(i, version=version_lib) for i in ['CampaignService', 'AdGroupService', 'AdGroupCriterionService']]


def campaing_IN(campList):

    '''
    Получаем список ID кампаний(CampaignStatus = ENABLED), по заданному AdWords ClienID (xxx-xxx-xxxx)
    AdWords ClienID берется из googleads.yaml, но можно и указать вручную
    '''

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
                'values': campList
                #'values': ['Brand','Brand_Pure_South','VendorTop','barbecue' 'VendorTop','barbecue','Сompetitor','Baby_food','Dacha_garden','GameToys']
            },
        ]}
    page = val_service[0].get(selector)  # val_service - моя переменная-список, см начало скрипта
    if 'entries' in page:
        return [campaign['id'] for campaign in page['entries']]
    else:
        print('No campaigns were found.')


def campaing_food():
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
                'operator': 'STARTS_WITH',
                'values': 'food'
            },
        ]}

    page = val_service[0].get(selector)  # val_service - моя переменная-список, см начало скрипта
    if 'entries' in page:
        return [campaign['id'] for campaign in page['entries']]
    else:
        print('No campaigns were found.')


def AdGroup_list( campaignIds):
    # получаем группы кампаний
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'IN',
                'values': campaignIds
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
    # Все это говно ниже надо выпилить и использовать:  тыр пыр for i in page['entries']
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


def keywords(adgroup_id):
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
                'field': 'CriterionUse',
                'operator': 'NOT_EQUALS',
                'values': ['NEGATIVE']
            },
            {
                'field': 'Status',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {# Берем ключи только со статусом "Допущено"
                'field': 'SystemServingStatus',
                'operator': 'EQUALS',
                'values': 'ELIGIBLE'
            }],
        # 'dateRange':{'min':'20170101', 'max':'20170730'},
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)},

        'ordering': [{'field': 'AdGroupId', 'sortOrder': 'ASCENDING'}]
    }
    page = val_service[2].get(selector)
    # print(page)
    more_pages = True
    d = {}
    while more_pages:
        if 'entries' in page:
            for keyword in page['entries']:
                # обрабатываем все варинаты ставок firstPositionCpc,topOfPageCpc != None
                # topOfPageCpc = None => firstPositionCpc = none
                # topOfPageCpc != None , но firstPositionCpc = None.
                # Делаем словарь из id группы и ids ключей
                if (keyword['firstPositionCpc'] is not None and keyword['topOfPageCpc'] is not None):
                    d.setdefault(keyword['adGroupId'], []).append([keyword['criterion']['id'], keyword['biddingStrategyConfiguration']['bids'][0]['bid']['microAmount'],
                                                                   keyword['firstPositionCpc']['amount']['microAmount'],
                                                                   keyword['topOfPageCpc']['amount']['microAmount'],
                                                                   keyword['firstPageCpc']['amount']['microAmount']])
                elif keyword['topOfPageCpc'] is None:
                    d.setdefault(keyword['adGroupId'], []).append([keyword['criterion']['id'], keyword['biddingStrategyConfiguration']['bids'][0]['bid']['microAmount'],0,0,
                                                                   keyword['firstPageCpc']['amount']['microAmount']])
                elif (keyword['topOfPageCpc'] is not None and keyword['firstPositionCpc'] is None):
                    d.setdefault(keyword['adGroupId'], []).append([keyword['criterion']['id'],keyword['biddingStrategyConfiguration']['bids'][0]['bid']['microAmount'],0,
                                                                   keyword['topOfPageCpc']['amount']['microAmount'],
                                                                   keyword['firstPageCpc']['amount']['microAmount']])
        else:
            print(keyword, 'No keywords were found.')

        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

    return d


def bid_update(ad_group_id, key_id, bidAmount, oldBid, position):
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
                            'microAmount': bidAmount
                        }}]}}}]

    val_service[2].mutate(operations)
    print(key_id, int(oldBid)/1000000, '->', int(bidAmount)/1000000, position)


def firstPositionCpc(group_list):
    for key, it in keywords(group_list).items():
        for i in it:
            if i[1] == i[2]:
                continue
            elif i[1] != i[2] and 0 < i[2] < 100000000:
                bid_update(key, i[0], str(i[2]), i[1], 'firstPositionCpc')
            elif i[3] != 0:
                bid_update(key, i[0], str(int((i[3]*1.05//10000)*10000)), i[1], 'topOfPageCpc')
            elif i[3] == 0 and i[4] != i[1]:
                bid_update(key, i[0], str(i[4]), i[1], 'firstPageCpc')


def topOfPageCpc(group_list, max_bid):
    for key, it in keywords(group_list).items():
        for i in it:
            if i[1] == i[3]:
                continue
            elif i[3] != i[1] and i[3] < max_bid:
                bid_update(key, i[0], str(int((i[3]*1.15//10000)*10000)), i[1], 'topOfPageCpc')
            else: bid_update(key, i[0], max_bid, i[1], str(max_bid/1000000)+'руб.')


def firstPageCpc(group_list):
    for key, it in keywords(group_list).items():
        for i in it:
            if i[1] == i[4]:
                continue
            elif i[4] != i[1] and i[4] < 80000000:
                bid_update(key, i[0], str(i[4]), i[1], 'firstPageCpc')
            else: bid_update(key, i[0], '80000000', i[1], '80руб.')


firstPosition = ['Brand', 'Brand_Pure_South']
topOfPage = ['GeneralTop']
firstPage = ['Zoo', 'House_kitchen', 'Health_beauty']

#группы капании  GeneralTop
GeneralTopProdukty = [54154261905, 54154262105, 54154265745, 54154260665, 54154265505, 54154265665,
                      54154262065, 54154262305, 54154262345, 54154265185, 54154261105, 54154265705, 54154266865,
                      ]
GeneralTopEda = [54154263105, 54154264305, 54154264945, 54154261345, 54154266625, 54154263065,
                 54154264265, 54154264505, 54154266385, 54154266705, 54154264225, 54154266465, 57432301673,
                 ]


def main( topP):
    max_bid = 150000000  # ограничение по ставке 90руб для topOfPageCpc
    for  j in [ topP]:
        campaignIds = campaing_IN(j)
        groupList = AdGroup_list(campaignIds)
        # if i == 0:
        #     continue#firstPositionCpc(groupList)
        # elif i == 1:
        topOfPageCpc(groupList, max_bid)
        # elif i == 2:
        #     firstPageCpc(groupList)


def mainFood():
    campaignIds = campaing_food()
    groupList = AdGroup_list(campaignIds)
    topOfPageCpc(groupList, 100000000)  # max_bid = 100руб


def mainGeneralTop():
    topOfPageCpc(GeneralTopProdukty, 110000000)  # 110руб
    topOfPageCpc(GeneralTopEda, 90000000)  # 90руб


main( topOfPage)
#mainFood()
# mainGeneralTop()
