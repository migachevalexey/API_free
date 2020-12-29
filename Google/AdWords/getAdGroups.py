from googleads import adwords


PAGE_SIZE = 500
CAMPAIGN_ID = [903408170,
               903408173,
               903408176
               ]



def main(client, campaign_id):
    # Initialize appropriate service.
    ad_group_service = client.GetService('AdGroupService', version='v201705')

    # Construct selector and get all ad groups.
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'IN',
                'values': [campaign_id]
            }
        ],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    more_pages = True

    while more_pages:
        page = ad_group_service.get(selector)

        # Display results.
        if 'entries' in page:
            for ad_group in page['entries']:
                print ('Ad group with name "%s", id "%s" and status "%s" was '
                       'found.' % (ad_group['name'], ad_group['id'],
                                   ad_group['status']))
        else:
            print ('No ad groups were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
    # Initialize client object.
    adwords_client = adwords.AdWordsClient.LoadFromStorage()

    main(adwords_client, CAMPAIGN_ID)