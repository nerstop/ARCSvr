# -*- coding:utf-8 -*-
__author__ = 'ery'

from datetime import timedelta


class CeleryConfigCommon(object):
    BROKER_URL = "redis://192.168.137.120:63709/5"
    CELERY_RESULT_BACKEND = "redis://192.168.137.120:63709/6"
    CELERY_ENABLE_UTC = False
    CELERY_ACCEPT_CONTENT = ["pickle", "json"]
    CELERY_REDIS_MAX_CONNECTIONS = 32

    CELERYBEAT_SCHEDULE = {
        "patrol_user_withdraw": {
            "task": "vind.patrol.user_withdraw",
            "schedule": timedelta(seconds=1)
        },
        "patrol_order_clean_outdated": {
            "task": "vind.patrol.order_clean_outdated",
            "schedule": timedelta(seconds=1)
        },
        "patrol_order_auto_complete": {
            "task": "vind.patrol.order_auto_complete",
            "schedule": timedelta(seconds=1)
        },
        "patrol_order_auto_confirm": {
            "task": "vind.patrol.order_auto_confirm",
            "schedule": timedelta(seconds=1)
        },
        "patrol_order_convert_to_public": {
            "task": "vind.patrol.order_convert_to_public",
            "schedule": timedelta(seconds=1)
        },
        "patrol_partner_clean_unaccepted": {
            "task": "vind.patrol.partner_clean_unaccepted",
            "schedule": timedelta(seconds=1)
        },
        "patrol_point_charge_clean_outdated": {
            "task": "vind.patrol.point_charge_clean_outdated",
            "schedule": timedelta(seconds=1)
        },
        "patrol_point_charge_sms_postprocessing": {
            "task": "vind.patrol.point_charge_sms_postprocessing",
            "schedule": timedelta(seconds=1)
        },
        "patrol_penaltylog": {
            "task": "vind.patrol.penaltylog",
            "schedule": timedelta(seconds=1)
        },
    }


class CeleryConfigDevelopment(CeleryConfigCommon):
    CELERY_REDIRECT_STDOUTS = True
    CELERY_REDIRECT_STDOUTS_LEVEL = "DEBUG"


class CeleryConfigProduction(CeleryConfigCommon):
    CELERY_REDIRECT_STDOUTS = False
    CELERY_REDIRECT_STDOUTS_LEVEL = "ERROR"


celery_configs = \
    {
        "development": CeleryConfigDevelopment,
        "production": CeleryConfigProduction,
    }
