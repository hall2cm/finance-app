import jwt
from jwt import algorithms
from werkzeug.exceptions import Forbidden, Unauthorized, InternalServerError
from functools import wraps
from flask import request, session
import sys


class CognitoAuth(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._token_name = app.config.get('TOKEN_COOKIE_NAME', '_auth_token')
        self._token_key_name = app.config.get('TOKEN_KEY_NAME', '_auth_key')
        self._jwk_key = app.config.get('JWK_KEY', None)

        self.user_callback = None
