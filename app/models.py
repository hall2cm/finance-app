from app import db, app
from hashlib import md5
from decimal import Decimal as D
import sqlalchemy.types as types
from sqlalchemy.sql import func
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import aliased
from sqlalchemy import update, text, and_
import pandas
from flask_login import UserMixin
import utils
import datetime
import sys
#from config import ACCESS_TOKEN, ID_TOKEN, CLIENT_ID


#class SqliteNumeric(types.TypeDecorator):
#    impl = types.String
#    def load_dialect_impl(self, dialect):
#        return dialect.type_descriptor(types.VARCHAR(100))
#    def process_bind_param(self, value, dialect):
#        return str(value)
#    def process_result_value(self, value, dialect):
#        return D(value)

# can overwrite the imported type name
# @note: the TypeDecorator does not guarantie the scale and precision.
# you can do this with separate checks

#Numeric = SqliteNumeric

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    aws_sub = db.Column(db.String(120), unique=True)
    cobrand_user_name = db.Column(db.String(120), unique=True)
    cobrand_password = db.Column(db.String(120))
    balance = db.relationship('Balance', backref='user', lazy='dynamic')
    transactions = db.relationship('Transactions', backref='user', lazy='dynamic')
    usersubcategory = db.relationship('UserSubCategory', backref='user', lazy='dynamic')
    userbudget = db.relationship('UserBudget', backref='user', lazy='dynamic')
    buckets = db.relationship('Buckets', backref='user', lazy='dynamic')
    useraccounts = db.relationship('UserAccounts', backref='user', lazy='dynamic')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id) # python 2
        except NameError:
            return str(self.id) # python 3

    def __repr__(self):
        return "<User(id='%r', email='%r', aws_sub='%r')>" % (self.id, self.email, self.aws_sub)


    def get_balance(user):
        for amount in Balance.query.filter_by(user=user):
            return amount.amount

    def get_amount(user):
        amount = db.session.query(func.sum(Transactions.amount).label('total_amount')).filter_by(user=user)
        for amount in amount.first():
            return amount

    def get_budget(user):
        all_budgets_df = pandas.read_sql((db.session.query(func.sum(Transactions.amount).label('total_amount')).\
                    join(Category).join(UserBudget).with_entities(UserBudget.name, Transactions.amount, UserBudget.budget_amount).\
                    group_by(UserBudget.name).filter(UserBudget.close_date == None, UserBudget.user_id == user.id, Transactions.user_id == user.id)).\
                    statement.apply_labels(), db.session.bind)

        budget_df = all_budgets_df
        return budget_df

    def get_buckets(user):
        buckets_df = pandas.read_sql((db.session.query(Buckets).with_entities(Buckets.name.label('Bucket Name'), Buckets.amount.label('Amount')).\
                    filter(Buckets.user_id == user.id)).statement.apply_labels(), db.session.bind)

        return buckets_df

    def get_transactions(user):
        df = pandas.read_sql((db.session.query(MintTransactions).with_entities(MintTransactions.date.label('Date'), MintTransactions.amount.label('Amount'),\
            MintTransactions.description.label('Merchant'), MintTransactions.notes.label('Notes')).order_by(MintTransactions.date.desc()).filter(MintTransactions.user_id == user.id)).\
            statement.apply_labels(), db.session.bind)
        return df


    def get_subcategory_choices(user, category):
        subcategory_choices = SubCategory.query.filter(SubCategory.category_id == category).with_entities(SubCategory.id, SubCategory.name).\
                                union(UserSubCategory.query.filter(UserSubCategory.category_id == category).filter_by(user=user).\
                                with_entities(UserSubCategory.id, UserSubCategory.name))
        return subcategory_choices.all()


    def write_budget_item(user, category, subcategory, budgetamount, date):
        if category != 0:
            budgetcategory = Category.query.get(category)
            if subcategory != 0:
                budgetsubcategory = SubCategory.query.get(subcategory)
                b = UserBudget(name=budgetsubcategory.name, is_budget=True, posting_date=date, budget_amount=budgetamount, user=user, categoryname=budgetcategory, subcategory=budgetsubcategory, created_date=date)
                db.session.add(b)
                db.session.commit()
            elif (subcategory == 0):
                b = UserBudget(name=budgetcategory.name, is_budget=True, posting_date=date, budget_amount=budgetamount, user=user, categoryname=budgetcategory, created_date=date)
                db.session.add(b)
                db.session.commit()
            return

    def get_drill_buckets(user, bucket_name):
        drilled_buckets_df = pandas.read_sql((db.session.query(Buckets).with_entities(Buckets.name.label('Bucket Name'), Buckets.amount.label('Amount'), Buckets.goal_amount.label('Goal Amount')).\
                            filter(Buckets.user_id==user.id, Buckets.name==bucket_name)).statement.apply_labels(), db.session.bind)
        return drilled_buckets_df


# db.session.query(Buckets).filter_by(id=3).update({'goal_amount': '700'})

#all_budgets_df = pandas.read_sql((db.session.query(func.sum(models.Transactions.amount).label('total_amount')).join(models.Category).join(models.UserBudget).with_entities(models.UserBudget.name, models.Transactions.amount, models.UserBudget.budget_amount).group_by(models.UserBudget.name).filter(models.UserBudget.close_date == None, models.UserBudget.user_id == 1, models.Transactions.user_id == 1)).statement.apply_labels(), db.session.bind)

#budget_df = pandas.read_sql((db.session.query(models.UserBudget.name, models.UserBudget.posting_date, models.UserBudget.close_date, models.UserBudget.budget_amount, time_diff).group_by(models.UserBudget.name, models.UserBudget.posting_date)).statement.apply_labels(), db.session.bind)
#time_diff = func.timestampdiff(text('MONTH'), models.UserBudget.posting_date, models.UserBudget.close_date)
# new_df = pandas.DataFrame(columns=['budgetname', 'budgetamount'])
#all_df = pandas.read_sql((db.session.query(models.UserBudget, func_sum).filter(models.UserBudget.user_id ==1).outerjoin(models.Category).outerjoin(models.SubCategory).outerjoin(models.Transactions, models.UserBudget.user_id == models.Transactions.user_id).with_entities(models.UserBudget.name, func_sum, models.UserBudget.budget_amount).group_by(models.UserBudget.name)).statement.apply_labels(), db.session.bind)
# print(str(all_df2.statement.compile(dialect=mysql.dialect()))
#func_sum = func.sum(func.coalesce(models.Transactions.amount,0) + func.coalesce(transactions_2,0))
#transactions_df = pandas.read_sql((db.session.query(UserBudget, func_sum).filter(models.UserBudget.user_id ==1, models.UserBudget.close_date != None).outerjoin(models.Transactions, and_(models.UserBudget.category_id == models.Transactions.category_id, models.UserBudget.user_id == models.Transactions.user_id)).outerjoin(transactions_2, and_(models.UserBudget.subcategory_id == transactions_2.subcategory_id,transactions_2.user_id == models.UserBudget.user_id)).with_entities(models.UserBudget.name, func_sum).group_by(models.UserBudget.name)).statement.apply_labels(), db.session.bind)

#func_sum = func.sum(func.coalesce(models.Transactions.amount,0) + func.coalesce(transactions_2,0))

#search = all_df[all_df['userbudget_name'].str.contains('General Savings')]
#search.sum_1.iat[0]


    def get_budget_amount(user):
        transactions_2 = aliased(Transactions)
        userbudget_df = pandas.DataFrame(columns=['budgetname', 'budgetamount'])
        final_df = pandas.DataFrame(columns=['budgetname', 'budgetamount', 'totalamount', 'transactionamount', 'totalbudgetamount', 'totaltransactionamount'])
        func_sum = func.sum(func.coalesce(Transactions.amount,0) + func.coalesce(transactions_2,0))
        current_date = datetime.date.today()
        posting_date = utils.get_posting_date(current_date)
        prior_date = utils.get_prior_posting(current_date)
        time_diff = func.timestampdiff(text('MONTH'), UserBudget.posting_date, UserBudget.close_date)+1
        time_diff2 = func.timestampdiff(text('MONTH'), UserBudget.posting_date, posting_date)+1
        param_dict = {"user": user.id, "prior_date": prior_date, "posting_date": posting_date}

        budget_df = pandas.read_sql((db.session.query(UserBudget.name, UserBudget.posting_date, UserBudget.close_date, UserBudget.budget_amount, time_diff.label('timediff_1'), time_diff2.label('timediff_2')).\
        group_by(UserBudget.name, UserBudget.posting_date).filter(UserBudget.user_id == user.id)).statement.apply_labels(), db.session.bind)

        transactions_posting_df = pandas.read_sql(('select userbudget.name,\
        sum(coalesce(transactions.amount, 0) + coalesce(transactions_1.amount, 0)) AS sum_1 FROM userbudget \
        LEFT OUTER JOIN (select (case when transaction_type = "debit" then amount*-1 else amount end) as amount, date, category_id, user_id from minttransactions \
        where date > %(prior_date)s  and date <= %(posting_date)s) as transactions \
        ON userbudget.category_id = transactions.category_id AND userbudget.user_id = transactions.user_id \
        and transactions.date > date_sub(userbudget.created_date, INTERVAL 1 MONTH) \
        LEFT OUTER JOIN (select (case when transaction_type = "debit" then amount*-1 else amount end) as amount, date, subcategory_id, user_id \
        from minttransactions where date > %(prior_date)s  and date <= %(posting_date)s) as transactions_1 \
        ON userbudget.subcategory_id = transactions_1.subcategory_id AND transactions_1.user_id = userbudget.user_id \
        and transactions_1.date > date_sub(userbudget.created_date, INTERVAL 1 MONTH) \
        WHERE userbudget.user_id = %(user)s and userbudget.close_date is null GROUP BY userbudget.name'),\
        con=db.engine, params=param_dict)

        transactions_df = pandas.read_sql(('select userbudget.name,\
        sum(coalesce(transactions.amount, 0) + coalesce(transactions_1.amount, 0)) AS sum_1 FROM userbudget \
        LEFT OUTER JOIN (select (case when transaction_type = "debit" then amount*-1 else amount end) as amount, date, category_id, user_id from minttransactions) as transactions \
        ON userbudget.category_id = transactions.category_id AND userbudget.user_id = transactions.user_id \
        and transactions.date > date_sub(userbudget.created_date, INTERVAL 1 MONTH) \
        LEFT OUTER JOIN (select (case when transaction_type = "debit" then amount*-1 else amount end) as amount, date, subcategory_id, user_id \
        from minttransactions) as transactions_1 \
        ON userbudget.subcategory_id = transactions_1.subcategory_id AND transactions_1.user_id = userbudget.user_id \
        and transactions_1.date > date_sub(userbudget.created_date, INTERVAL 1 MONTH) \
        WHERE userbudget.user_id = %(user)s and userbudget.close_date is null GROUP BY userbudget.name'),\
        con=db.engine, params=param_dict)

        for index, row in budget_df.iterrows():
            if row['userbudget_close_date'] != None:
                amount = row['userbudget_budget_amount'] * row['timediff_1']
                name = row['userbudget_name']
                df = pandas.DataFrame([[name, amount]], columns=['budgetname', 'budgetamount'])
                userbudget_df = userbudget_df.append(df, ignore_index=True)
            elif row['userbudget_close_date'] == None:
                amount = row['userbudget_budget_amount'] * row['timediff_2']
                name = row['userbudget_name']
                df = pandas.DataFrame([[name, amount]], columns=['budgetname', 'budgetamount'])
                userbudget_df = userbudget_df.append(df, ignore_index=True)
        userbudget_df = userbudget_df.groupby(['budgetname'], as_index=False)[['budgetamount']].sum()

        for index, row in userbudget_df.iterrows():
            name = row['budgetname']
            search = transactions_df[transactions_df['name'].str.contains(name)]
            search1 = transactions_posting_df[transactions_posting_df['name'].str.contains(name)]
            search2 = budget_df[budget_df['userbudget_name'].str.contains(name)]
            amount = search.sum_1.iat[0]
            amount1 = search1.sum_1.iat[0]
            amount2 = search2.userbudget_budget_amount.iat[0]
            final_amount = row['budgetamount'] + amount
            budgetamount = row['budgetamount']
            df = pandas.DataFrame([[name, amount2, final_amount, amount1, budgetamount, amount]], columns=['budgetname', 'budgetamount','totalamount', 'transactionamount', 'totalbudgetamount', 'totaltransactionamount'])
            final_df = final_df.append(df, ignore_index=True)

        return final_df



class Balance(db.Model):
    __tablename__ = 'balance'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(40))
    amount = db.Column(db.Numeric(16,2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Balance(id='%r', account='%r', amount='%r')>" % (self.id, self.account, self.amount)

class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    is_budget = db.Column(db.Boolean, default=False)
    posting_date = db.Column(db.DateTime)
    close_date = db.Column(db.DateTime)
    budget_amount = db.Column(db.Numeric(16,2))
    subcategory = db.relationship('SubCategory', backref='categoryname', lazy='dynamic')
    usersubcategory = db.relationship('UserSubCategory', backref='categoryname', lazy='dynamic')
    transactions = db.relationship('Transactions', backref='categoryname', lazy='dynamic')
    userbudget = db.relationship('UserBudget', backref='categoryname', lazy='dynamic')

    def __repr__(self):
        return "<Category(name='%r', is_budget='%r', budget_amount='%r', posting_date='%r', close_date='%r')>" % (self.name, self.is_budget, self.budget_amount, self.posting_date, self.close_date)

class SubCategory(db.Model):
    __tablename__ = 'subcategory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    is_budget = db.Column(db.Boolean, default=False)
    posting_date = db.Column(db.DateTime)
    close_date = db.Column(db.DateTime)
    budget_amount = db.Column(db.Numeric(16,2))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    transactions = db.relationship('Transactions', backref='subcategory', lazy='dynamic')
    userbudget = db.relationship('UserBudget', backref='subcategory', lazy='dynamic')

    def __repr__(self):
        return "<SubCategory(id='%r', name='%r', is_budget='%r', budget_amount='%r', posting_date='%r', close_date='%r')>" % (self.id, self.name, self.is_budget, self.budget_amount, self.posting_date, self.close_date)


class UserSubCategory(db.Model):
    __tablename__= 'usersubcategory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    is_budget = db.Column(db.Boolean, default=False)
    posting_date = db.Column(db.DateTime)
    close_date = db.Column(db.DateTime)
    budget_amount = db.Column(db.Numeric(16,2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    transactions = db.relationship('Transactions', backref='usersubcategory', lazy='dynamic')
    userbudget = db.relationship('UserBudget', backref='usersubcategory', lazy='dynamic')

    def __repr__(self):
        return "<UserSubCategory(id='%r', name='%r', is_budget='%r', budget_amount='%r', user_id='%r', posting_date='%r', close_date='%r')>" % (self.id, self.name, self.is_budget, self.budget_amount, self.user_id, self.posting_date, self.close_date)


class UserBudget(db.Model):
    __tablename__= 'userbudget'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    is_budget = db.Column(db.Boolean, default=False)
    posting_date = db.Column(db.DateTime)
    close_date = db.Column(db.DateTime)
    budget_amount = db.Column(db.Numeric(16,2))
    created_date = db.Column(db.DateTime)
    is_bucket = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    usersubcategory_id = db.Column(db.Integer, db.ForeignKey('usersubcategory.id'))
    buckets = db.relationship('Buckets', backref='userbudget', lazy='dynamic')

    def __repr__(self):
        return "<UserSubCategory(id='%r', name='%r', is_budget='%r', budget_amount='%r', user_id='%r', posting_date='%r', close_date='%r', created_date='%r', category_id='%r', subcategory_id='%r', usersubcategory_id='%r')>" % \
        (self.id, self.name, self.is_budget, self.budget_amount, self.user_id, self.posting_date, self.close_date, self.created_date, self.category_id, self.subcategory_id, self.usersubcategory_id)

class Transactions(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(40))
    date = db.Column(db.DateTime)
    original_description = db.Column(db.String(500))
    split_type = db.Column(db.String(40))
    category = db.Column(db.String(40))
    currency = db.Column(db.String(10))
    amount = db.Column(db.Numeric(16,2))
    user_description = db.Column(db.String(500))
    memo = db.Column(db.String(500))
    classification = db.Column(db.String(100))
    account_name = db.Column(db.String(100))
    simple_description = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    usersubcategory_id = db.Column(db.Integer, db.ForeignKey('usersubcategory.id'))

    def __repr__(self):
        return "<Transactions(Status='%r', Date='%r', Original Description='%r', Amount='%f', Category='%r', Account Name='%r')>" % (
                self.status, self.date.strftime("%m/%d/%y"), self.original_description, self.amount, self.category, self.account_name)

class MintTransactions(db.Model):
    __tablename__ = 'minttransactions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    description = db.Column(db.String(500))
    original_description = db.Column(db.String(500))
    amount = db.Column(db.Numeric(16,2))
    transaction_type = db.Column(db.String(20))
    category = db.Column(db.String(100))
    account_name = db.Column(db.String(100))
    labels = db.Column(db.String(40))
    notes = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    usersubcategory_id = db.Column(db.Integer, db.ForeignKey('usersubcategory.id'))

    def __repr__(self):
        return "<MintTransactions(id='%r', Date='%r', Description='%r', Original Description='%r', Amount='%f', Transaction Type='%r', Category='%r', Account Name='%r', labels='%r', notes='%r')>" % (
                self.id, self.date, self.description, self.original_description, self.amount, self.transaction_type, self.category, self.account_name, self.labels, self.notes)


class Buckets(db.Model):
    __tablename__ = 'buckets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    amount = db.Column(db.Numeric(16,2))
    goal_amount = db.Column(db.Numeric(16,2))
    userbudget_id = db.Column(db.Integer, db.ForeignKey('userbudget.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Buckets(id='%r', Name='%r', Amount='%r', Goal Amount='%r')>" % (
                self.id, self.name, self.amount, self.goal_amount)


class UserAccounts(db.Model):
    __tablename__='useraccounts'

    id = db.Column(db.Integer, primary_key=True)
    posting_date = db.Column(db.DateTime)
    CONTAINER = db.Column(db.String(40))
    accountName = db.Column(db.String(40))
    accountNumber = db.Column(db.String(40))
    accountStatus = db.Column(db.String(40))
    accountType = db.Column(db.String(40))
    availableBalanceamount = db.Column(db.Numeric(16,2))
    availableCashamount = db.Column(db.Numeric(16,2))
    availableCreditamount = db.Column(db.Numeric(16,2))
    balanceamount = db.Column(db.Numeric(16,2))
    createdDate = db.Column(db.DateTime)
    currentBalanceamount = db.Column(db.Numeric(16,2))
    accountid = db.Column(db.String(40))
    includeInNetWorth = db.Column(db.String(40))
    isAsset = db.Column(db.String(40))
    isManual = db.Column(db.String(40))
    lastRefreshAttempt = db.Column(db.DateTime)
    lastRefreshed = db.Column(db.DateTime)
    lastUpdated = db.Column(db.DateTime)
    name = db.Column(db.String(40))
    nextRefreshScheduled = db.Column(db.DateTime)
    providerAccountId = db.Column(db.String(40))
    providerId = db.Column(db.String(40))
    providerName = db.Column(db.String(40))
    statusCode = db.Column(db.String(40))
    statusMessage = db.Column(db.String(40))
    totalCashLimitamount = db.Column(db.Numeric(16,2))
    totalCreditLineamount = db.Column(db.Numeric(16,2))
    url = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return "<UserAccounts(CONTAINER='%r', posting_date='%r', accountName='%r', accountNumber='%r', accountStatus='%r', accountType='%r', availableBalanceamount='%r',\
        availableCashamount='%r', availableCreditamount='%r', balanceamount='%r', createdDate='%r', currentBalanceamount='%r',\
        accountid='%r', includeInNetWorth='%r', isAsset='%r', isManual='%r', lastRefreshAttempt='%r', lastRefreshed='%r', lastUpdated='%r', \
        name='%r', nextRefreshScheduled='%r', providerAccountId='%r', providerId='%r', providerName='%r', statusCode='%r', statusMessage='%r', \
        totalCashLimitamount='%r', totalCreditLineamount='%r', url='%r')>" % (
        self.CONTAINER, self.posting_date, self.accountName, self.accountNumber, self.accountStatus, self.accountType, self.availableBalanceamount,\
        self.availableCashamount, self.availableCreditamount, self.balanceamount, self.createdDate, self.currentBalanceamount,\
        self.accountid, self.includeInNetWorth, self.isAsset, self.isManual, self.lastRefreshAttempt, self.lastRefreshed, self.lastUpdated, \
        self.name, self.nextRefreshScheduled, self.providerAccountId, self.providerId, self.providerName, self.statusCode, self.statusMessage, \
        self.totalCashLimitamount, self.totalCreditLineamount, self.url)
