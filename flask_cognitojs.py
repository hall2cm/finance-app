import jwt
from jwt import algorithms
from werkzeug.exceptions import Forbidden, Unauthorized, InternalServerError
from functools import wraps
from flask import request, session, flash, redirect, url_for
import sys


REASON_NO_KEY = u'Token Authentication Failed: No Key.'

class CognitoAuth(object):

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._token_name = app.config.get('TOKEN_COOKIE_NAME', '_auth_token')
        self._token_key_name = app.config.get('TOKEN_KEY_NAME', '_auth_key')
        self._jwk_key = app.config.get('JWK_KEY', None)

        self.login_view = app.config.get('LOGIN_URL', None)


    def require_token(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.cookies.get(self._token_name)
            key = self.get_key()
            if key is not None:
                try:
                    access_info = jwt.decode(auth, self._token_key_name)
                except ValueError:
                    # Will return ValueError if it can't unserialize key data i.e. bad key.
                    flash("Please Login")
                    if self.login_view is not None:
                        return redirect(url_for('login'))
                    raise Unauthorized(description=REASON_NO_KEY)
                except (jwt.DecodeError, jwt.ExpiredSignatureError):
                    # Will return DecodeError if the signiture verification failed
                    flash("Please Login")
                    if self.login_view is not None:
                        return redirect(url_for('login'))
                    raise Unauthorized(description=REASON_NO_KEY)
                aws_sub = access_info['sub']
                session['user_id'] = aws_sub
                return f(*args, **kwargs)
            raise InternalServerError(description=REASON_NO_KEY)
        return decorated


    def get_key(self):
        if self._jwk_key is not None:
            self._token_key_name = algorithms.RSAAlgorithm.from_jwk(self._jwk_key)
            return self._token_key_name
        self._token_key_name = None
        return self._token_key_name


    def create_user(self):
        auth = request.cookies.get(self._token_name)
        key = self.get_key()
        if key is not None:
            try:
                access_info = jwt.decode(auth, self._token_key_name)
            except ValueError:
                # Will return ValueError if it can't unserialize key data i.e. bad key.
                flash("An error occurred, please try again")
                if self.login_view is not None:
                    return redirect(url_for('login'))
                raise Unauthorized(description=REASON_NO_KEY)
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                # Will return DecodeError if the signiture verification failed
                flash("An error occurred, please try again")
                if self.login_view is not None:
                    return redirect(url_for('login'))
                raise Unauthorized(description=REASON_NO_KEY)
            aws_sub = access_info['sub']
            username = access_info['username']
            return aws_sub, username
        raise InternalServerError(description=REASON_NO_KEY)
