from googleads import adwords

AD_GROUP_ID = [59999154710]

CRITERION_ID = [329019765284]


def main(client, ad_group_id, criterion_id):
    client.partial_failure = True # Обработка неудавшихся  операций. Что бы чушь всякую не писало
    # Initialize appropriate service.
    ad_group_criterion_service = client.GetService(
        'AdGroupCriterionService', version='v201710')

    # Construct operations and update bids.
    for j in AD_GROUP_ID:
        for i in criterion_id:
            # try:
                operations = [{
                    'operator': 'SET',
                    'operand': {
                        'xsi_type': 'BiddableAdGroupCriterion',
                        'adGroupId': j,
                        'criterion': {
                            'id': i,
                        },
                        'biddingStrategyConfiguration': {
                            'bids': [
                                {
                                    'xsi_type': 'CpcBid',
                                    'bid': {
                                        'microAmount': '10000'} }
                            ]
                        }
                    }
                }]
                ad_group_criteria = ad_group_criterion_service.mutate(operations)
            # except: continue
    #Display results.
    if 'value' in ad_group_criteria:
        for criterion in ad_group_criteria['value']:
            print(criterion['criterion'])
            if criterion['criterion']['Criterion.Type'] == 'Keyword':
                print ('Ad group criterion with ad group id "%s" and criterion id '
                       '"%s" currently has bids:'
                       % (criterion['adGroupId'], criterion['criterion']['id']))
                for bid in criterion['biddingStrategyConfiguration']['bids']:
                    print ('\tType: "%s", value: %s' % (bid['Bids.Type'], bid['bid']['microAmount']))
    else:
        print ('No ad group criteria were updated.')

if __name__ == '__main__':
    adwords_client = adwords.AdWordsClient.LoadFromStorage('C:\Python\googleads.yml')
    #adwords_client = adwords.AdWordsClient.LoadFromStorage()
    main(adwords_client, AD_GROUP_ID, CRITERION_ID)