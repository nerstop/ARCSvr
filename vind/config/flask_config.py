# -*- coding:utf-8 -*-
__author__ = 'ery'


class FlaskConfig:
    SECRET_KEY = "8E2B5526F773806D93E185162DC10F87C5E4117CA7C73ACB8BDD36D164E23C970D4A1D0F80891E2784B1CA95447E847818E997991DE9398F6A2D683A46FA4067"
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5
    SESSION_TYPE = "redis"
    UPLOAD_FOLDER = "/vind/vind/tmp"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(FlaskConfig):
    DEBUG = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class ProductionConfig(FlaskConfig):
    DEBUG = False
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


flask_config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
