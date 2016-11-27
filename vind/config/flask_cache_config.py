# -*- coding:utf-8 -*-
__author__ = 'ery'


flask_cache_configs =\
    {
        "Redis":
            {
                "CACHE_TYPE": "redis",
                "CACHE_DEFAULT_TIMEOUT": 300,
                "CACHE_KEY_PREFIX": "FlaSkcAcHE__",
                # "CACHE_REDIS_HOST": "192.168.137.120",
                # "CACHE_REDIS_PORT": 63709,
                # "CACHE_REDIS_DB": 3,
                # "CACHE_REDIS_URL": "redis://192.168.137.120:63709/3"
                "CACHE_REDIS_URL": "unix:///tmp/redis.sock?db=3"
            },
        "Simple":
            {
                "CACHE_TYPE": "simple",
                "CACHE_DEFAULT_TIMEOUT": 300,
                "CACHE_THRESHOLD": 1024,
            },
    }