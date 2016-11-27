# -*- coding:utf-8 -*-
__author__ = 'ery'

import os
import time
from datetime import datetime
from uuid import uuid4
try:
    import cPickle as pickle
except ImportError:
    import pickle

from flask.sessions import SessionInterface as FlaskSessionInterface
from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import Signer, BadSignature


class CustomRedisSession(object):
    def __init__(self, app=None, connect_kw=None):
        self.app = app
        self.connect_kw = connect_kw
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # print("init_app")
        app.session_interface = self._get_interface(app)

    def _get_interface(self, app):
        config = app.config.copy()
        config.setdefault('SESSION_TYPE', 'null')
        config.setdefault('SESSION_USE_SIGNER', False)
        config.setdefault('SESSION_KEY_PREFIX', 'session:')
        config.setdefault('SESSION_REDIS', None)
        # config.setdefault('SESSION_MEMCACHED', None)
        # config.setdefault('SESSION_FILE_DIR',
        #                   os.path.join(os.getcwd(), 'flask_session'))
        # config.setdefault('SESSION_FILE_THRESHOLD', 500)
        # config.setdefault('SESSION_FILE_MODE', 384)
        # config.setdefault('SESSION_MONGODB', None)
        # config.setdefault('SESSION_MONGODB_DB', 'flask_session')
        # config.setdefault('SESSION_MONGODB_COLLECT', 'sessions')
        config.setdefault('SESSION_SQLALCHEMY', None)
        config.setdefault('SESSION_SQLALCHEMY_TABLE', 'sessions')

        session_interface = RedisSessionInterface(
            config['SESSION_REDIS'], config['SESSION_KEY_PREFIX'],
            config['SESSION_USE_SIGNER'], self.connect_kw)

        return session_interface


def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds


class ServerSideSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.permanent = True
        self.modified = False


class RedisSession(ServerSideSession):
    pass


class SessionInterface(FlaskSessionInterface):

    def _generate_sid(self):
        return str(uuid4())

    def _get_signer(self, app):
        if not app.secret_key:
            return None
        return Signer(app.secret_key, salt='flask-session',
                      key_derivation='hmac')


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis, key_prefix, use_signer=False, connect_kw=None):
        if redis is None:
            from redis import Redis
            if not connect_kw:
                redis = Redis()
            else:
                redis = Redis(**connect_kw)
        self.redis = redis
        self.key_prefix = key_prefix
        self.use_signer = use_signer

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid)
        if self.use_signer:
            signer = self._get_signer(app)
            if signer is None:
                return None
            try:
                sid = signer.unsign(sid)
            except BadSignature:
                sid = None

        val = self.redis.get(self.key_prefix + sid)
        if val is not None:
            try:
                data = self.serializer.loads(val)
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid)
        return self.session_class(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        if not session:
            if session.modified:
                self.redis.delete(self.key_prefix + session.sid)
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        # Modification case.  There are upsides and downsides to
        # emitting a set-cookie header each request.  The behavior
        # is controlled by the :meth:`should_set_cookie` method
        # which performs a quick check to figure out if the cookie
        # should be set or not.  This is controlled by the
        # SESSION_REFRESH_EACH_REQUEST config flag as well as
        # the permanent flag on the session itself.
        # if not self.should_set_cookie(app, session):
        #    return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.key_prefix + session.sid, val,
                         total_seconds(app.permanent_session_lifetime))
        if self.use_signer:
            session_id = self._get_signer(app).sign(session.sid)
        else:
            session_id = session.sid
        response.set_cookie(app.session_cookie_name, session_id,
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)