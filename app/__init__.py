from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_webpack import Webpack
from flask_login import LoginManager
from flask_httpauth import HTTPBasicAuth
from flask_cognitojs import CognitoAuth
from flask_session import Session

webpack = Webpack()
lm = LoginManager()
#auth = HTTPBasicAuth()
cognito = CognitoAuth()
sess = Session()

application = Flask(__name__)
app = application
app.config.from_object('config')
db = SQLAlchemy(app)
webpack.init_app(app)
lm.init_app(app)
cognito.init_app(app)
sess.init_app(app)

from app import views, models
