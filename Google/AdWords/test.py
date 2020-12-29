import logging
import sys
from googleads import adwords

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)


def main(client):

    report_downloader = client.GetReportDownloader(version='v201710')

    report = {
        'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
        'dateRangeType': 'LAST_7_DAYS',
        'reportType': 'CRITERIA_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['CampaignId', 'AdGroupId', 'Id', 'CriteriaType',
                       'Criteria', 'Impressions', 'Clicks', 'Cost', 'CpcBid' , 'TopOfPageCpc', 'FirstPageCpc']
        }
    }

    # You can provide a file object to write the output to. For this demonstration
    # we use sys.stdout to write the report to the screen.
    report_downloader.DownloadReport(
        report, sys.stdout, skip_report_header=True, skip_column_header=False,
        skip_report_summary=False, include_zero_impressions=True, )


if __name__ == '__main__':
    # adwords_client = adwords.AdWordsClient.LoadFromStorage()
    adwords_client = adwords.AdWordsClient.LoadFromStorage('C:\Python\Training\API\Google\AdWords\googleads.yml')
    main(adwords_client)

    from googleads import adwords


# REPORT_TYPE = 'CRITERIA_PERFORMANCE_REPORT'
#
#
# def main(client, report_type):
#     # Initialize appropriate service.
#     report_definition_service = client.GetService(
#         'ReportDefinitionService', version='v201705')
#
#     # Get report fields.
#     fields = report_definition_service.getReportFields(report_type)
#
#     # Display results.
#     print ('Report type "%s" contains the following fields:' % report_type)
#     for field in fields:
#         print (' - %s (%s)' % (field['fieldName'], field['fieldType']))
#         if 'enumValues' in field:
#             print ('  := [%s]' % ', '.join(field['enumValues']))
#
#
# if __name__ == '__main__':
#     # Initialize client object.
#     adwords_client = adwords.AdWordsClient.LoadFromStorage()
#
#     main(adwords_client, REPORT_TYPE)

adgroup_id=[111111]
def main(client, adgroup_id):
    PAGE_SIZE = 500
    # Initialize appropriate service.
    client.partial_failure = True
    ad_group_criterion_service = client.GetService(
        'AdGroupCriterionService', version='v201705')

    # Construct selector and get all ad group criteria.
    offset = 0
    selector = {
        'fields': ['Id', 'CriteriaType', 'KeywordMatchType', 'KeywordText', 'FirstPageCpc', 'CpcBid', 'TopOfPageCpc','FirstPositionCpc' ],
        'predicates': [
            {
                'field': 'AdGroupId',
                'operator': 'IN',
                'values': [adgroup_id]
            },
            {
                'field': 'CriteriaType',
                'operator': 'EQUALS',
                'values': ['KEYWORD']
            }
        ],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        },
        'ordering': [{'field': 'Id', 'sortOrder': 'ASCENDING'}]
    }
    page = ad_group_criterion_service.get(selector)
    # print(page)
    # Display results.
    if 'entries' in page:
        for keyword in page['entries']:
            print('GroupId {}: Keyword ID - {}, type {}, text - {}. \nFirstPageCpc - {}руб; Текущая ставка - {}руб'.format(
                keyword['adGroupId'],
                keyword['criterion']['id'],
                keyword['criterion']['type'],
                keyword['criterion']['text'],
                #keyword['criterion']['matchType'],
                keyword['firstPageCpc']['amount']['microAmount']/1000000,
                keyword['biddingStrategyConfiguration']['bids'][0]['bid']['microAmount']/1000000
            ))
            print('=--------------------')
        else:
            print ('No keywords were found.')
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])


if __name__ == '__main__':
    # adwords_client = adwords.AdWordsClient.LoadFromStorage()
    adwords_client = adwords.AdWordsClient.LoadFromStorage('C:\Python\Training\API\Google\AdWords\googleads.yml')
    # adwords_client.SetClientCustomerId('123-456-7890')

    main(adwords_client, ADGROUP_ID)

