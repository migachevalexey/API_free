from googleads import adwords
import re

'''

'''

version_lib = 'v201802'
adwords_client = adwords.AdWordsClient.LoadFromStorage('C:\Python\googleads.yml')
service = adwords_client.GetService('AdGroupService', version=version_lib)

CAMPAIGN_Ids = [1403970386]


def AdGroup_Dict(campaignIds):
    selector = {
        'fields': ['Id', 'Name'],
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
    }
    page = service.get(selector)

    return {i['id']: i['name'] for i in page['entries']}


def main(groupIdName):
    j = 0
    re_string = r'\d{,4}\|[a-zA-Z]{0,8}_\d{,2} '
    for k,(key, items) in enumerate(groupIdName.items(), start=1):
        # Construct operations and update an ad group.

        operations = [{
            'operator': 'SET',
            'operand': {
                'id': key,
                'name': re.sub(re_string, '', items)}}]

        try:
         service.mutate(operations)
        except:
            operations = [{
                'operator': 'SET',
                'operand': {
                    'id': key,
                    'name': re.sub(re_string, '', items) + f'_{j}'
                }}]
            j += 1
            service.mutate(operations)


AD_GROUP_ID = AdGroup_Dict(CAMPAIGN_Ids)
main(AD_GROUP_ID)
