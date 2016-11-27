# -*- coding:utf-8 -*-
__author__ = 'ery'

# try:
#    import uwsgi
# except ImportError:
#    import pip
#    pip.main(["install", "uwsgi-stub==0.1.2"])
#    import uwsgi

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
basedir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(basedir, "../../"))

import redis
import random
from datetime import datetime, timedelta
from vind.tools import Singleton
from vind.config import redis_server_settings


class PsuedoCached(object):
    __metaclass__ = Singleton

    d = None

    def __init__(self):
        if not self.d:
            self.d = {}

    def get(self, key):
        if key in self.d:
            if self.d[key]["expire"] >= datetime.now():
                return self.d[key]["value"]
            else:
                self.d.pop(key, None)
                return None
        else:
            return None

    def set(self, key, value, expire):
        self.d[key] = {"value": value, "expire": datetime.now() + timedelta(seconds=expire)}
        return True

    def clear(self):
        self.d = {}

    def ping(self):
        return True

    def get_many(self, get_list):
        found_dict = {}
        not_found_list = []
        for idx in range(get_list.__len__()):
            _value = self.get(get_list[idx])
            if not _value:
                not_found_list.append(get_list[idx])
            else:
                found_dict[get_list[idx]] = _value
        return found_dict, not_found_list


class RedisCached(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._connection_pool = \
            redis.ConnectionPool(max_connections=512, connection_class=redis.UnixDomainSocketConnection, \
                                 **redis_server_settings["LocalSetting"])
        self._r = redis.Redis(connection_pool=self._connection_pool)

    def get(self, key):
        return self._r.get(key)

    def set(self, key, value, expire):
        return self._r.setex(key, value, int(expire))

    def clear(self):
        self._r.flushdb()
        return True

    def ping(self):
        try:
            self._r.ping()
        except redis.RedisError as e:
            print(e.message, str(e.args))
            return False
        return True

    def get_many(self, get_list):
        found_dict = {}
        not_found_list = []
        p = self._r.pipeline()
        for idx in range(get_list.__len__()):
            p.get(get_list[idx])
        _values = p.execute()
        for idx in range(get_list.__len__()):
            if not _values[idx]:
                not_found_list.append(get_list[idx])
            else:
                found_dict[get_list[idx]] = _values[idx]
        return found_dict, not_found_list


class LocalCacheManager(object):
    __metaclass__ = Singleton

    def __init__(self, default_expire_mean=30, default_expire_dev=None):

        self.bucket = RedisCached()
        if not self.bucket.ping():
            print("PsuedoCached()")
            self.bucket = PsuedoCached()

        self.default_expire_mean = default_expire_mean
        if not default_expire_dev:
            self.default_expire_dev = default_expire_mean / 8.
        else:
            self.default_expire_dev = default_expire_dev

    def _gen_expire(self):
        return random.normalvariate(self.default_expire_mean, self.default_expire_dev)

    def get(self, key):
        return self.bucket.get(key)

    def set(self, key, value):
        return self.bucket.set(key, value, self._gen_expire())

    def clear(self):
        self.bucket.clear()
        return True

    def get_many(self, get_list):
        return self.bucket.get_many(get_list)
