import requests
import pandas
import utils
import datetime




class Cobrand():

    def __init__(self, cobrand_user_name, cobrand_user_password):
        self.cobrand_login = 'sbCobhall2cm'
        self.cobrand_password = '07eaef76-e091-4d1a-ba72-aac0d4075ef8'
        self.cobrand_url = 'https://developer.api.yodlee.com/ysl/restserver/v1/cobrand/login'
        self.user_url = 'https://developer.api.yodlee.com/ysl/restserver/v1/user/login'
        self.account_url = 'https://developer.api.yodlee.com/ysl/restserver/v1/accounts'
        self.holdings_url = 'https://developer.api.yodlee.com/ysl/restserver/v1/holdings'
        self.transactions_url = 'https://developer.api.yodlee.com/ysl/restserver/v1/transactions'
        self.cob_session = None
        self.cobrand_user_name = cobrand_user_name
        self.cobrand_user_password = cobrand_user_password
        self.user_session = None

    def get_cob_session(self):
        login_data = {'cobrandLogin': self.cobrand_login, 'cobrandPassword': self.cobrand_password, 'locale': 'en_US'}
        r = requests.post(self.cobrand_url, data=login_data)
        r_json = r.json()
        self.cob_session = 'cobSession=' + r_json['session']['cobSession']
        print(self.cob_session)

    def get_user_session(self):
        login_data = {'password': self.cobrand_user_password, 'loginName': self.cobrand_user_name, 'locale': 'en_US'}
        headers = {'Authorization': self.cob_session}
        r = requests.post(self.user_url, data=login_data, headers=headers)
        r_json = r.json()
        print(r_json)
        self.user_session = 'userSession=' + r_json['user']['session']['userSession']
        print(self.user_session)

    def get_accounts(self):
        current_date = datetime.date.today()
        posting_date = utils.get_posting_date(current_date)
        header_data = self.cob_session + ',' + self.user_session
        headers = {'Authorization': header_data}
        r = requests.get(self.account_url, headers=headers)
        r_json = r.json()
        #print(r_json)
        for account in r_json['account']:
            for key, val in account['refreshinfo'].items():
                account[key] = val
            del account['refreshinfo']
            for key, val in account['balance'].items():
                account['balance' + key] = val
            del account['balance']
            del account['balancecurrency']
            if account['CONTAINER'] == 'creditCard':
                for key, val in account['availableCash'].items():
                    account['availableCash' + key] = val
                del account['availableCash']
                del account['availableCashcurrency']
                for key, val in account['availableCredit'].items():
                    account['availableCredit' + key] =  val
                del account['availableCredit']
                del account['availableCreditcurrency']
                for key, val in account['totalCashLimit'].items():
                    account['totalCashLimit' + key] =  val
                del account['totalCashLimit']
                del account['totalCashLimitcurrency']
                for key, val in account['totalCreditLine'].items():
                    account['totalCreditLine' + key] = val
                del account['totalCreditLine']
                del account['totalCreditLinecurrency']
            elif account['CONTAINER'] == 'bank':
                for key, val in account['availableBalance'].items():
                    account['availableBalance' + key] =  val
                del account['availableBalance']
                del account['availableBalancecurrency']
                for key, val in account['currentBalance'].items():
                    account['currentBalance' + key] = val
                del account['currentBalance']
                del account['currentBalancecurrency']
                for dct in account['holderProfile']:
                    for key, val in dct['name'].items():
                        account['name'] = val
                del account['holderProfile']
        df = pandas.DataFrame.from_dict(r_json['account'])
        df['posting_date'] = posting_date
        df['user_id'] = session['user_id']
        df.rename(columns={'id': 'accountid'}, inplace=True)
        update_db_accounts(df)


    def update_db_accounts(self, df):
        aws_sub = session['user_id']
        user = User.query.filter_by(aws_sub=aws_sub).first()
        for index, row in df.iterrows():
            posting_date = row['posting_date']
            useraccount = UserAccounts.query.filter_by(aws_sub=aws_sub, user_id=user.id, posting_date=posting_date)
            if useraccount.count() > 0:
                db.session.delete(useraccount)
                db.session.commit()
        df.to_sql('useraccounts', con=db.engine, flavor='mysql', if_exists='append', index=False)




'''
lastUpdated
providerName
lastRefreshed
nextRefreshScheduled
statusCode
statusMessage
lastRefreshAttempt
accountType
id
totalCreditLine
includeInNetWorth
accountNumber
url
availableCredit
accountNumber
accountName
accountStatus
providerAccountId
holderProfile
availableBalance
CONTAINER
balance
createdDate
availableCash
currentBalance
isAsset
totalCashLimit
providerId
isManual

CONTAINER
accountName
accountNumber
accountStatus
accountType
availableBalanceamount
availableCashamount
availableCreditamount
balanceamount
createdDate
currentBalanceamount
id
includeInNetWorth
isAsset
isManual
lastRefreshAttempt
lastRefreshed
lastUpdated
name
nextRefreshScheduled
providerAccountId
providerId
providerName
statusCode
statusMessage
totalCashLimitamount
totalCreditLineamount
url

{'lastUpdated': '2017-01-24T10:58:57Z', 'providerName': 'Dag Site', 'refreshinfo': {'lastRefreshed': '2017-01-24T10:58:57Z', 'nextRefreshScheduled': '2017-01-31T12:24:05Z', 'statusCode': 0, 'statusMessage': 'OK', 'lastRefreshAttempt': '2017-01-24T10:58:57Z'}, 'accountType': 'OTHER', 'id': 10328819, 'totalCreditLine': {'currency': 'USD', 'amount': 3000}, 'url': 'BILL_VALID', 'availableCredit': {'currency': 'USD', 'amount': 1363}, 'includeInNetWorth': True, 'accountNumber': '************8614', 'accountName': 'CREDIT CARD', 'accountStatus': 'ACTIVE', 'providerAccountId': 10156514, 'createdDate': '2016-12-09T20:44:17Z', 'availableCash': {'currency': 'USD', 'amount': 600}, 'CONTAINER': 'creditCard', 'balance': {'currency': 'USD', 'amount': 1636.44}, 'totalCashLimit': {'currency': 'USD', 'amount': 600}, 'isAsset': False, 'providerId': '16441', 'isManual': False}
{'lastUpdated': '2017-01-24T10:58:57Z', 'providerName': 'Dag Site', 'refreshinfo': {'lastRefreshed': '2017-01-24T10:58:57Z', 'nextRefreshScheduled': '2017-01-30T18:06:53Z', 'statusCode': 0, 'statusMessage': 'OK', 'lastRefreshAttempt': '2017-01-24T10:58:57Z'}, 'accountType': 'SAVINGS', 'id': 10328818, 'includeInNetWorth': True, 'accountNumber': '503-5623xxx', 'accountName': 'TESTDATA1', 'accountStatus': 'ACTIVE', 'providerAccountId': 10156514, 'holderProfile': [{'name': {'displayed': 'accountHolder'}}], 'availableBalance': {'currency': 'USD', 'amount': 65454.78}, 'CONTAINER': 'bank', 'balance': {'currency': 'USD', 'amount': 9044.78}, 'createdDate': '2016-12-09T20:44:16Z', 'currentBalance': {'currency': 'USD', 'amount': 9044.78}, 'isAsset': True, 'providerId': '16441', 'isManual': False}
'''

'''
#Cobrand login [POST]
data = {'cobrandLogin': 'sbCobhall2cm', 'cobrandPassword': '07eaef76-e091-4d1a-ba72-aac0d4075ef8', 'locale': 'en_US'}
url = 'https://developer.api.yodlee.com/ysl/restserver/v1/cobrand/login'
r = requests.post(url, data=data)
'''
'''
Response will be like
{\n  "cobrandId" : 10010352,
\n  "applicationId" : "3A4CAE9B71A1CCD7FF41F51006E9ED00",
\n  "locale" : "en_US",
\n  "session" :
        {\n    "cobSession" : "08062013_0:6aaf8d3a47b73d60641deb3dfca80ba7c1f1536d492a40c620923f191d3920bd8fd8dc251d246d4fe3fe926b8aae059d6990ec69d11706a3cd4080c43e203383"\n  }
\n}
'''

'''
#user login [POST]
data = {'password': 'sbMemhall2cm1#123', 'loginName': 'sbMemhall2cm1', 'locale': 'en_US'}
# cobSession comes from the response of the cobrand login
headers = {'Authorization': 'cobSession=08062013_0:6aaf8d3a47b73d60641deb3dfca80ba7c1f1536d492a40c620923f191d3920bd8fd8dc251d246d4fe3fe926b8aae059d6990ec69d11706a3cd4080c43e203383'}
url = 'https://developer.api.yodlee.com/ysl/restserver/v1/user/login'
r = requests.post(url, data=data, headers=headers)
'''
'''
Response will be like this
'{"user":
{"id":10077455,"loginName":"sbMemhall2cm1","name":
{"first":"Cory","last":"Hall"},
"session":{"userSession":"08062013_1:a1d10b7fbe46c740d930fc8f251d7820f8c271f3fe8dbb21ea1279e3d59ccd936756532346d6641f177ad52211282f7f30186ea7bd794eb45f6abcf5b4e5e38a"},
"preferences":{"currency":"USD","timeZone":"PST","dateFormat":"MM/dd/yyyy"}}}'
'''
'''
#get accounts [GET]
#The get accounts service provides information about accounts added by the user.
#By default, this service returns information for active and to be closed accounts.
url = 'https://developer.api.yodlee.com/ysl/restserver/v1/accounts'
#need to cobsession token from cobrand login and usersession token from user login
headers = {'Authorization':
'cobSession=08062013_0:6aaf8d3a47b73d60641deb3dfca80ba7c1f1536d492a40c620923f191d3920bd8fd8dc251d246d4fe3fe926b8aae059d6990ec69d11706a3cd4080c43e203383, \
userSession=08062013_1:a1d10b7fbe46c740d930fc8f251d7820f8c271f3fe8dbb21ea1279e3d59ccd936756532346d6641f177ad52211282f7f30186ea7bd794eb45f6abcf5b4e5e38a'}
r = requests.get(url, headers=headers)
'''


'''
Response will be like this
{"account":[
    {"CONTAINER":"creditCard",
        "providerAccountId":10156514,
        "isManual":false,
        "accountName":"CREDIT CARD",
        "accountStatus":"ACTIVE",
        "url":"BILL_VALID",
        "accountNumber":"************8614",
        "isAsset":false,
        "balance":
            {"amount":1636.44, "currency":"USD"},
        "id":10328819,
        "lastUpdated":"2017-01-24T10:58:57Z",
        "includeInNetWorth":true,
        "providerId":"16441",
        "providerName":"Dag Site,
        "accountType":"OTHER",
        "availableCash":
            {"amount":600,"currency":"USD"},
        "availableCredit":
            {"amount":1363,"currency":"USD"},
        "totalCashLimit":
            {"amount":600,"currency":"USD"},
        "totalCreditLine":
            {"amount":3000,"currency":"USD"},
        "createdDate":"2016-12-09T20:44:17Z",
        "refreshinfo":
            {"statusCode":0,
            "statusMessage":"OK",
            "lastRefreshed":"2017-01-24T10:58:57Z",
            "lastRefreshAttempt":"2017-01-24T10:58:57Z",
            "nextRefreshScheduled":"2017-01-31T12:24:05Z"}
    },
    {"CONTAINER":"bank",
        "providerAccountId":10156514,
        "isManual":false,
        "accountName":"TESTDATA1",
        "accountStatus":"ACTIVE",
        "accountNumber":"503-5623xxx",
        "isAsset":true,
        "balance":
            {"amount":9044.78,"currency":"USD"},
        "id":10328818,
        "lastUpdated":"2017-01-24T10:58:57Z",
        "includeInNetWorth":true,
        "providerId":"16441",
        "providerName":"Dag Site",
        "availableBalance":
            {"amount":65454.78,"currency":"USD"},
        "currentBalance":
            {"amount":9044.78,"currency":"USD"},
        "accountType":"SAVINGS",
        "createdDate":"2016-12-09T20:44:16Z",
        "refreshinfo":
            {"statusCode":0,
            "statusMessage":"OK",
            "lastRefreshed":"2017-01-24T10:58:57Z",
            "lastRefreshAttempt":"2017-01-24T10:58:57Z",
            "nextRefreshScheduled":"2017-01-30T18:06:53Z"},
        "holderProfile":[
            {"name":
                {"displayed":"accountHolder"}
            }
        ]
    },
    {"CONTAINER":"bank",
        "providerAccountId":10156514,
        "isManual":false,
        "accountName":"TESTDATA",
        "accountStatus":"ACTIVE",
        "accountNumber":"503-1123xxx",
        "isAsset":true,
        "balance":
            {"amount":44.78,"currency":"USD"},
        "id":10328817,
        "lastUpdated":"2017-01-24T10:58:57Z",
        "includeInNetWorth":true,
        "providerId":"16441",
        "providerName":"Dag Site",
        "availableBalance":
            {"amount":54.78,"currency":"USD"},
        "currentBalance":
            {"amount":44.78,"currency":"USD"},
        "accountType":"CHECKING",
        "createdDate":"2016-12-09T20:44:16Z",
        "refreshinfo":
            {"statusCode":0,
            "statusMessage":"OK",
            "lastRefreshed":"2017-01-24T10:58:57Z",
            "lastRefreshAttempt":"2017-01-24T10:58:57Z",
            "nextRefreshScheduled":"2017-01-30T18:06:53Z"},
        "holderProfile":[
            {"name":
                {"displayed":"accountHolder"}
            }
        ]
    }
]}
'''

# get holdings [GET]
'''
The get holdings service is used to get the list of holdings of a user.
Supported holding types can be employeeStockOption,
moneyMarketFund, bond, etc. and is obtained using get holding type list service.
Asset classifications for the holdings need to be requested through the "include" parameter.
Asset classification information for holdings are not available by default, as it is a premium feature.
'''
'''
#need to cobsession token from cobrand login and usersession token from user login
headers = {'Authorization':
'cobSession=08062013_0:6aaf8d3a47b73d60641deb3dfca80ba7c1f1536d492a40c620923f191d3920bd8fd8dc251d246d4fe3fe926b8aae059d6990ec69d11706a3cd4080c43e203383, \
userSession=08062013_1:a1d10b7fbe46c740d930fc8f251d7820f8c271f3fe8dbb21ea1279e3d59ccd936756532346d6641f177ad52211282f7f30186ea7bd794eb45f6abcf5b4e5e38a'}
url = 'https://developer.api.yodlee.com/ysl/restserver/v1/holdings'
r = requests.post(url, data=data, headers=headers)
'''
'''
Response will be like this

'''

#get transactions [GET]
'''
The Transaction service is used to get a list of transactions for a user.
By default, this service returns the last 30 days of transactions from today's date.
Values for categoryId parameter can be fetched from get transaction category list service.
The categoryId is used to filter transactions based on system-defined category as well as user-defined category.
User-defined categoryIds should be provided in the filter with the prefix "U". E.g. U10002
The skip and top parameters are useful for paginating transactions (i.e., to fetch small transaction
payloads for performance reasons)
Double quotes in the merchant name will be prefixed by backslashes (\) in the response,
e.g. Toys \"R\" Us.
Note 1.Category input is deprecated and replaced with categoryId. 2. The address field in the response is available only when the TDE key is turned on.
'''
'''
#need to cobsession token from cobrand login and usersession token from user login
headers = {'Authorization':
'cobSession=08062013_0:6aaf8d3a47b73d60641deb3dfca80ba7c1f1536d492a40c620923f191d3920bd8fd8dc251d246d4fe3fe926b8aae059d6990ec69d11706a3cd4080c43e203383, \
userSession=08062013_1:a1d10b7fbe46c740d930fc8f251d7820f8c271f3fe8dbb21ea1279e3d59ccd936756532346d6641f177ad52211282f7f30186ea7bd794eb45f6abcf5b4e5e38a'}
url = 'https://developer.api.yodlee.com/ysl/restserver/v1/transactions'
r = requests.post(url, data=data, headers=headers)
'''
'''
Response will be like this

'''
