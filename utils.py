import pandas, numpy
import datetime
import calendar
import re
import sys

def get_posting_date(date):
    current_month = date.month
    current_year = date.year
    calendar_day = calendar.monthrange(current_year, current_month)
    last_day = calendar_day[1]
    posting_date = date.replace(day=last_day)
    return posting_date

def get_prior_posting(date):
    current_month = date.month
    current_year = date.year
    if current_month == 1:
        prior_month = 12
        prior_year = current_year - 1
    elif current_month != 1:
        prior_month = current_month - 1
        prior_year = current_year
    calendar_day = calendar.monthrange(prior_year, prior_month)
    last_day = calendar_day[1]
    prior_posting = date.replace(day=last_day, month=prior_month, year=prior_year)
    return prior_posting
