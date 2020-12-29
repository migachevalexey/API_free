import logging
from io import StringIO
import sys
from googleads import adwords


logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

# The chunk size used for the report download.
CHUNK_SIZE = 16 * 1024


def main(client):
    report_downloader = client.GetReportDownloader(version='v201705')

    # Create report definition.
    report = {
        'reportName': 'Last 7 days CRITERIA_PERFORMANCE_REPORT',
        'dateRangeType': 'LAST_7_DAYS',
        'reportType': 'CRITERIA_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['CampaignId', 'AdGroupId', 'Id', 'CriteriaType',
                       'Criteria', 'Impressions', 'Clicks', 'Cost']
        }
    }

    # Retrieve the report stream and print it out
    report_data = StringIO()
    stream_data = report_downloader.DownloadReportAsStream(
        report, skip_report_header=False, skip_column_header=False,
        skip_report_summary=False, include_zero_impressions=True)

    try:
        while True:
            chunk = stream_data.read(CHUNK_SIZE)
            if not chunk: break
            report_data.write(chunk.decode() if sys.version_info[0] == 3
                                                and getattr(report_data, 'mode', 'w') == 'w' else chunk)
        print (report_data.getvalue())
    finally:
        report_data.close()
        stream_data.close()


if __name__ == '__main__':
    adwords_client = adwords.AdWordsClient.LoadFromStorage()
    main(adwords_client)