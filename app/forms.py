#from flask.ext.wtf import Form
from flask_wtf import Form
#from wtforms import StringField, BooleanField, TextAreaField, SelectField, DecimalField, TextField, PasswordField
from wtformsparsleyjs import StringField, BooleanField, TextAreaField, SelectField, DecimalField, PasswordField
from wtforms.validators import DataRequired, Length, InputRequired, Optional, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

class UploadForm(Form):
    upload = FileField('csv', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV only!')
    ])

class BudgetForm(Form):
    budgetcategory = SelectField(u'Budget Category', coerce=int, choices=[], validators=[
        InputRequired(message=(u'Please enter a valid Category'))
    ])
    budgetsubcategory = SelectField(u'Budget SubCategory', coerce=int, choices=[(0,0)], validators=[
        Optional()
    ])
    budgetamount = DecimalField(u'Budget Amount', places=2, validators=[
        InputRequired(message=(u'Please enter a budget amount'))
    ])
    #userbudgetcategory = TextField(u'Custom SubCategory', validators=[
    #    Optional()
    #])

class LoginForm(Form):
    email = StringField(u'Email', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField(u'Password', validators=[
        DataRequired()
    ])

class SignUpForm(Form):
    email = StringField(u'Email', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField(u'New Password', validators=[
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField(u'Confirm Password')
