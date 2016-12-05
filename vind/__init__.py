# -*- coding:utf-8 -*-
__author__ = 'ery'

import logging
streamFormatter = logging.Formatter("%(asctime)s [%(levelname)-8s|%(process)d|%(name)s] > %(message)s")
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(streamFormatter)

# 여기에서 로거를 선언한다. 종합 출력은 이 루트 로거를 통해서 수행되게 된다.
root_logger = logging.getLogger()
root_logger.addHandler(streamHandler)
root_logger.setLevel(logging.DEBUG)

sqlalchemy_logger = logging.getLogger("sqlalchemy")
# sqlalchemy_logger.setLevel(logging.DEBUG)
sqlalchemy_logger.setLevel(logging.WARNING)

connection_pool_logger = logging.getLogger("vind.connection_pool")
connection_pool_logger.setLevel(logging.DEBUG)

try:
    from gevent import monkey
except ImportError:
    # gevent 가 아예 없다는 뜻.
    pass
else:
    # gevent 1.1 이상부터 지원.
    targets = ["__builtin__", "_threading_local", "_gevent_saved_patch_all", "socket", "thread", "ssl", "signal",
               "subprocess", "threading", "time", "os", "select"]
    check_is_patched = monkey.is_module_patched
    is_patched = False
    root_logger.debug("##### Gevent Patch Info #####")
    for target in targets:
        if check_is_patched(target):
            is_patched = True
            root_logger.debug("[O] %s" % (target,))
        else:
            root_logger.debug("[X] %s" % (target,))

import datetime

from flask import Flask, session, escape, jsonify
from flask.ext.cache import Cache
from vind.config import flask_config, redis_server_settings, flask_cache_configs
app = Flask(__name__)
cache = Cache(app, config=flask_cache_configs["Redis"])

from vind.tools import CustomRedisSession

flask_session_obj = CustomRedisSession(app, redis_server_settings["Session"])

def create_app():
    OPERATION_MODE = "development"
    app.config.from_object(flask_config[OPERATION_MODE])
    flask_config[OPERATION_MODE].init_app(app)

    app.config["SESSION_TYPE"] = flask_config[OPERATION_MODE].SESSION_TYPE
    app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(seconds=7200)

    # from vind.controllers import (settings_bp, users_bp, management_bp, \
    #                                version_bp, terms_bp, price_bp, \
    #                                address_bp, event_bp, notification_bp, \
    #                                interest_address_bp, mypage_bp, order_bp, \
    #                                partner_bp, point_bp, point_charge_bp, point_withdraw_bp, \
    #                                ad_bp, tax_bp)
    from vind.controllers import (hello_bp, intro_bp)

    # register blueprints.
    blueprints = [v for k, v in locals().items()
                  if str(k).endswith("_bp")]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # 플래스크용 로거를 얻는다.
    # 기본적으로 루트 로거로 흘려보내게 선언된다.
    # __name__ = "vind"
    flask_logger = logging.getLogger(__name__)
    flask_logger.propagate = True

    if OPERATION_MODE == "development":
        # sqlalchemy_logger.setLevel(logging.DEBUG)
        sqlalchemy_logger.setLevel(logging.WARNING)
        sqlalchemy_logger.info("setLevel(logging.DEBUG)")

        flask_logger.setLevel(logging.DEBUG)

        connection_pool_logger.setLevel(logging.DEBUG)
    elif OPERATION_MODE == "production":
        sqlalchemy_logger.setLevel(logging.WARNING)
        sqlalchemy_logger.info("setLevel(logging.WARNING)")

        flask_logger.setLevel(logging.WARNING)

        connection_pool_logger.setLevel(logging.INFO)

    return app
