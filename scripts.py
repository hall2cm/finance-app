import pandas, numpy
from app import models, db
import datetime
import calendar
import re
import sys
import jwt
from jwt import algorithms
from config import ACCESS_TOKEN, ID_TOKEN, CLIENT_ID


class UploadFile:

    df = pandas.read_sql(('select id, name from category'), con=db.engine)
    df3 = pandas.read_sql(('select id, name, category_id from subcategory'), con=db.engine)

    def __init__(self, file, userid):
        self.df2 = pandas.read_csv(file, parse_dates=[0])
        self.userid = userid

    def update_file(self):
        self.df2.columns = self.df2.columns.str.replace(' ', '_')
        #self.df2['Amount'] = self.df2.Amount.str.replace(',', '')
        self.df2['user_id'] = self.userid

    def search_category(self):
        for category in self.df2['Category']:
            if len(re.split('\s+|/', category)) == 1:
                first = re.split('\s+|/', category)[0]
                search_first = self.df3[self.df3['name'].str.contains(first)]
                if not search_first.empty:
                    self.update_df(search_first, self.df2, category)
                else:
                    category_search_first = self.df[self.df['name'].str.contains(first)]
                    if not category_search_first.empty:
                        self.update_df_category(category_search_first, self.df2, category)

            elif len(re.split('\s+|/', category)) == 2:
                first = re.split('\s+|/', category)[0]
                second = re.split('\s+|/', category)[1]
                search_first = self.df3[self.df3['name'].str.contains(first)]
                search_second = self.df3[self.df3['name'].str.contains(second)]
                category_search_first = self.df[self.df['name'].str.contains(first)]
                category_search_second = self.df[self.df['name'].str.contains(second)]
                if search_first.id.count() == 1:
                    self.update_df(search_first, self.df2, category)
                elif (search_first.id.count() > 1 or search_first.id.count() < 1) and search_second.id.count() == 1:
                    self.update_df(search_second, self.df2, category)
                elif (search_first.empty or search_first.id.count() != 1) and (search_second.empty or search_second.id.count() != 1):
                    if category_search_first.id.count() == 1:
                        self.update_df_category(category_search_first, self.df, category)
                    elif (category_search_first.id.count() > 1 or category_search_first.id.count() < 1) and category_search_second.id.count() == 1:
                        self.update_df_category(category_search_second, self.df, category)

            elif len(re.split('\s+|/', category)) == 3:
                first = re.split('\s+|/', category)[0]
                second = re.split('\s+|/', category)[1]
                third = re.split('\s+|/', category)[2]
                search_first = self.df3[self.df3['name'].str.contains(first)]
                search_second = self.df3[self.df3['name'].str.contains(second)]
                search_third = self.df3[self.df3['name'].str.contains(third)]
                category_search_first = self.df[self.df['name'].str.contains(first)]
                category_search_second = self.df[self.df['name'].str.contains(second)]
                category_search_third = self.df[self.df['name'].str.contains(third)]
                if search_first.id.count() == 1:
                    self.update_df(search_first, self.df2, category)
                elif (search_first.id.count() > 1 or search_first.id.count() < 1)\
                        and search_second.id.count() == 1 and search_second.name.iat[0] != 'and':
                    self.update_df(search_second, self.df2, category)
                elif search_third.id.count() == 1:
                    self.update_df(search_third, self.df2, category)
                elif (search_first.empty or search_first.id.count() != 1) and (search_second.empty or search_second.id.count() != 1) and (search_third.empty or search_third.id.count() != 1):
                    if category_search_first.id.count() == 1:
                        self.update_df_category(category_search_first, self.df2, category)
                    elif (category_search_first.id.count() > 1 or category_search_first.id.count() < 1)\
                            and category_search_second.id.count() == 1 and category_search_second.name.iat[0] != 'and':
                        self.update_df_category(category_search_second, self.df2, category)
                    elif category_search_third.id.count() == 1:
                        self.update_df_category(category_search_third, self.df2, category)
        return self.df2

    def write_file(self):
        self.df2.to_sql('transactions', con=db.engine, flavor='mysql', if_exists='append', index=False)

    def write_mint_file(self):
        self.df2.to_sql('minttransactions', con=db.engine, flavor='mysql', if_exists='append', index=False)

    def update_df(self, search, df2, category):
        category_id = search.category_id.iat[0]
        subcategory_id = search.id.iat[0]
        self.df2.loc[self.df2['Category'] == category, 'category_id'] = str(category_id)
        self.df2.loc[self.df2['Category'] == category, 'subcategory_id'] = str(subcategory_id)
        return self.df2

    def update_df_category(self, search, df2, category):
        category_id = search.id.iat[0]
        self.df2.loc[self.df2['Category'] == category, 'category_id'] = str(category_id)
        return self.df2







class AuthClass:

    def __init__(self, access_token, id_token):
        self.access_token = access_token
        self.id_token = id_token
        self.access_public_key = algorithms.RSAAlgorithm.from_jwk(ACCESS_TOKEN)
        self.id_public_key = algorithms.RSAAlgorithm.from_jwk(ID_TOKEN)
        self.client_id = CLIENT_ID

    def authorize_user(self):
        access_info = jwt.decode(self.access_token, self.access_public_key)
        id_info = jwt.decode(self.id_token, self.id_public_key, audience=self.client_id)
        aws_sub = access_info['sub']
        username = id_info['cognito:username']
        return (aws_sub, username)

def require_token(func):
    @wraps(func)
    def check_token(*args, **kwargs):
        if 'access_token' not in session:
            return Response("Access Denied")
