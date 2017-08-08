from app import app, db, cognito, sess, lm
import pandas
import numpy
from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from .models import User, Balance, Transactions, Category, SubCategory, UserSubCategory
from .forms import UploadForm, BudgetForm, LoginForm, SignUpForm
import sys
import scripts
import utils
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER
from scripts import UploadFile, AuthClass
import datetime
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps




@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(user_id):
    return User.query.filter_by(aws_sub=user_id).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    loginform = LoginForm()
    signupform = SignUpForm()
    return render_template('login2.html',
                            title='Sign In',
                            loginform=loginform,
                            signupform=signupform)

@app.route('/_logout', methods=['GET', 'POST'])
def logout():
    user_email = g.user.email
    session.clear()
    return jsonify(user_email)


@app.route('/_authenticate', methods=['POST', 'GET'])
def authenticate():
    return url_for('index')

@app.route('/_add_user', methods=['POST'])
def get_user():
    aws_sub, username = cognito.create_user()
    user = User(email=username, aws_sub=aws_sub)
    db.session.add(user)
    db.session.commit()
    return url_for('login')



@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@cognito.require_token
def index():
    print(g.user, file=sys.stderr)
    user = g.user
    print(user, file=sys.stderr)
    balance = g.user.get_balance()
    amount = g.user.get_amount()
    form = UploadForm()
    return render_template('index.html',
                            title='Home',
                            user=user,
                            balance=balance,
                            amount=amount,
                            form=form)


@app.route('/upload', methods=['GET', 'POST'])
@cognito.require_token
def upload():
    form = UploadForm()
    userid = g.user.id
    #for userid in user_id.first():
        #userid = userid
    if form.validate_on_submit():
        file = form.upload.data
        read = UploadFile(file, userid)
        read.update_file()
        read.search_category()
        read.write_mint_file()
        flash('File Uploaded!')
        return redirect(url_for('index'))
    flash('Invalid File')
    return redirect(url_for('index'))

@app.route('/budget', methods=['GET', 'POST'])
@cognito.require_token
def budget():
    balance = g.user.get_balance()
    budget = g.user.get_budget_amount()
    form = BudgetForm()
    form.budgetcategory.choices = [(0, '--- Select One ---')] + [(category.id, category.name) for category in Category.query.order_by(Category.name)]
    return render_template('budget.html',
                            title='Budget',
                            budget = budget,
                            balance = balance,
                            form = form
                            )

@app.route('/transactions', methods=['GET', 'POST'])
@cognito.require_token
def transactions():
    balance = g.user.get_balance()
    transaction = g.user.get_transactions()
    return render_template('transactions.html',
                            title='Transactions',
                            transaction = transaction,
                            balance = balance
                            )

@app.route('/_subcategory', methods=['GET'])
@cognito.require_token
def subcategory():
    form = BudgetForm()
    categoryid = request.args.get('categoryid')
    choices = g.user.get_subcategory_choices(categoryid)
    form.budgetsubcategory.choices = [(0, '')] + choices
    choices.insert(0, (0, ''))
    return jsonify(choices)

@app.route('/_get_selected', methods=['GET'])
@cognito.require_token
def get_selected():
    form = BudgetForm()
    subcategoryid = request.args.get('subcategoryid', 0)
    subcategoryname = request.args.get('subcategoryname', None)
    return jsonify(subcategoryid)

@app.route('/_submit_budget', methods=['GET', 'POST'])
@cognito.require_token
def submit_budget():
    form = BudgetForm()
    user_id = User.query.with_entities(User.id).filter_by(email=g.user.email)
    userid = user_id[0]
    current_date = datetime.date.today()
    posting_date = utils.get_posting_date(current_date)
    categoryid = form.budgetcategory.data
    choices = g.user.get_subcategory_choices(categoryid)
    form.budgetsubcategory.choices = [(0, '')] + choices
    form.budgetcategory.choices = [(0, '--- Select One ---')] + [(category.id, category.name) for category in Category.query.order_by(Category.name)]
    if form.validate_on_submit():
        budgetcategory = form.budgetcategory.data
        budgetsubcategory = form.budgetsubcategory.data
        #userbudgetcategory = form.userbudgetcategory.data
        budgetamount = form.budgetamount.data
        if budgetcategory != 0:
            g.user.write_budget_item(budgetcategory, budgetsubcategory, budgetamount, posting_date)
        return redirect(url_for('budget'))
    flash(form.budgetcategory.errors)
    #flash(form.userbudgetcategory.errors)
    flash(form.budgetsubcategory.errors)
    flash(form.budgetamount.errors)
    return redirect(url_for('budget'))

@app.route('/buckets', methods=['GET', 'POST'])
@cognito.require_token
def buckets():
    balance = g.user.get_balance()
    buckets = g.user.get_buckets()
    return render_template('buckets.html',
                            buckets = buckets,
                            balance = balance,
                            title='Buckets')

@app.route('/_get_budget', methods=['GET'])
@cognito.require_token
def get_budget():
    budget = g.user.get_budget_amount()
    budget_json = budget.to_json()
    return jsonify(budget_json)

@app.route('/_get_buckets', methods=['GET'])
@cognito.require_token
def get_buckets():
    buckets_df = g.user.get_buckets()
    buckets_json = buckets_df.to_json()
    return jsonify(buckets_json)

@app.route('/_drill_buckets', methods=['GET'])
@cognito.require_token
def drill_buckets():
    bucket_name = request.args.get('bucket_name')
    drilled_buckets_df = g.user.get_drill_buckets(bucket_name)
    drilled_buckets_json = drilled_buckets_df.to_json()
    return jsonify(drilled_buckets_json)
