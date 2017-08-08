#-*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://draega:0Malazan27@budgetdb.cbacvexar4dj.us-east-1.rds.amazonaws.com:3306/budgetdb'
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = False

WEBPACK_MANIFEST_PATH = os.path.join(basedir + "/build", 'manifest.json')

UPLOAD_FOLDER = os.path.join(basedir, 'tmp')
ALLOWED_EXTENSIONS = set(['csv'])

SESSION_TYPE = 'sqlalchemy'

JWK_KEY = '{"alg":"RS256","e":"AQAB","kid":"oc4WvlKDy83l1gWbsbSU0f8qQpD2yV4KfhMbdTWT1Xs=","kty":"RSA","n":"nYi7YYD2qr4kHgZf-vEtDXPXsmnvR3TI5O0Ljgw0OEpTh2MBnzhC7SbktV02FCo53HN0BQhBLNeTV76RIMOn19tnPJVD3DfKuUE2kn3p7u38aoGVfaDBTvqRJlmCyddUKWubDnuBOVK6kvJ3Vj3Gd1bHPB_j4qBHvCgy9mGqifMVsxURqoALfNHGq97iUl8ikjSRMWNuomZ5brnpXVEINBme5CJ2TySPiDyyvdcV_aVWme5f4XGYr7nVaJVK-JgIZn0bc0qOJsdHcssjj5NRSEHzQInBXs0NESoywxe_H1WJJlKaRYUzFu42mIT9jY24nH-OyjjAtcz0BCfiaq_OQw","use":"sig"}'
ID_TOKEN = '{"alg":"RS256","e":"AQAB","kid":"MuZh2WUBpbHL/DLgxcobsTo97El8BShPwq6XtxITKb4=","kty":"RSA","n":"ikQCXxp2cz61QxKeR9tSd1-fIg8AVdHFMeZ6qdiBGB65avknnQFVyZY_CDxSQVJPqWEreVmEa7mhdAVUhvK7b2Cc7jmZaousuDJQfNTR2cIS3ps1xJ1QSTZ7l6l2kXK7wdFoHRDwvFNdrI3PKH7nQc2dZ2Xm1aHUs8AdESskp28fXzESIyZiwSfiwx4uKg2mDoFynvzqdP2D5UIvY1SRspfu3wI0qcFxMGywMG-NeOnT_wcJKVIpTUMgLIfgmQndfo-Og5-Z55fayh_0krSOgE7Obn2QLP4BnOH0MVOQsk3zqqL08cOmmUl9AAdOd4O_6cU_W_LGJrm6zQs2lq1WBQ","use":"sig"}'
CLIENT_ID = '7rttjsr0mhv2g3ci227kkf48t1'
ACCESS_TOKEN = ''

LOGIN_URL = 'login'
