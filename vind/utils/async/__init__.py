# -*- coding:utf-8 -*-
__author__ = 'ery'

import sys
import imp

imp.reload(sys)
sys.setdefaultencoding("utf-8")
import os
os.environ["SQLALCHEMY_SILENT"] = "1"

basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir, "../../../"))

from datetime import datetime, timedelta
from celery import Celery, Task, signals
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from flask import current_app

from vind.tools import *
from vind.config import celery_configs


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
    print("##### Gevent Patch Info #####")
    for target in targets:
        if check_is_patched(target):
            is_patched = True
            print("[O] %s" % (target,))
        else:
            print("[X] %s" % (target,))

# class CeleryConfig(object):
#     BROKER_URL = "redis://192.168.137.120:63709/5"
#     # BROKER_URL = "amqp://guest:passwd@192.168.137.120:56702/"
#     CELERY_RESULT_BACKEND = "redis://192.168.137.120:63709/6"
#     CELERY_ENABLE_UTC = False
#     # CELERY_ACCEPT_CONTENT = ["pickle", "json", "msgpack", "yaml"]
#     CELERY_ACCEPT_CONTENT = ["pickle", "json"]
#     CELERY_REDIS_MAX_CONNECTIONS = 32
#     CELERY_REDIRECT_STDOUTS = False
#     CELERY_REDIRECT_STDOUTS_LEVEL = "DEBUG"

capp = Celery(current_app, include=["message",])
# capp.config_from_object(CeleryConfig)
is_production = False
if is_production:
    capp.config_from_object(celery_configs["production"], force=True)
else:
    capp.config_from_object(celery_configs["development"], force=True)
logger = get_task_logger(__name__)


class BaseTask(Task):
    abstract = True
    ignore_result = False
    default_retry_delay = 3


class NoResultTask(Task):
    abstract = True
    ignore_result = True
    default_retry_delay = 3
