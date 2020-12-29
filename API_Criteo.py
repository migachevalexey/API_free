from pycriteo import Client


c = Client('xxx@gmail.com', 'KY3', '61')

campaigns = c.getCampaigns({'budgetIDs':50854})
categorie = c.getCategories({'categoryIDs': []})
Budget = c.getBudgets({'budgetIDs':[]})
Statistics= c.getStatisticsLastUpdate()

# print(Budget.budget, Budget)
# print(Statistics)
# print(campaigns)

z = dict(campaigns.campaign[0])
p=list(z.keys())[0]
['status',
 'campaignID',
 'categoryBids',
 'budgetID',
 'campaignName',
 'remainingDays',
 'campaignBid']
print(p)

job = c.scheduleReportJob(
    {'reportType': 'Campaign',
     'selectedColumns': ['clicks'],
     'reportSelector': {
         'CampaignIDs': [i.campaignID for i in campaigns.campaign]

     },
     'startDate': '2017-05-05',
     'endDate': '2017-07-10',
     'isResultGzipped': False,
     'aggregationType': 'Daily'
     })
# print(job)
# print(job.jobID)
# zz= c.getJobStatus(job.jobID)
# print(zz)

# c.downloadReport(job.jobID, '123.csv')
# job2 = c.getCategories({'budgetIDs': []})

# print(job2)