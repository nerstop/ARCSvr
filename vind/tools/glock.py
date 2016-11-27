# -*- coding:utf-8 -*-
__author__ = 'ery'

import redis
from os import urandom
from hashlib import sha1

from redis import StrictRedis
from redis.exceptions import NoScriptError
from vind.config import redis_server_settings
from vind.tools import Singleton

UNLOCK_SCRIPT = b"""
    if redis.call("get", KEYS[1]) == ARGV[1] then
        redis.call("del", KEYS[2])
        redis.call("lpush", KEYS[2], 1)
        return redis.call("del", KEYS[1])
    else
        return 0
    end
"""
UNLOCK_SCRIPT_HASH = sha1(UNLOCK_SCRIPT).hexdigest()


class AlreadyAcquired(RuntimeError):
    pass


class NotAcquired(RuntimeError):
    pass


# class AlreadyStarted(RuntimeError):
#     pass


# class TimeoutNotUsable(RuntimeError):
#     pass


# class InvalidTimeout(RuntimeError):
#     pass


# class TimeoutTooLarge(RuntimeError):
#     pass


class RLockConnection(object):
    __metaclass__ = Singleton

    def __init__(self, max_connections=128):
        self._connection_pool = \
            redis.ConnectionPool(max_connections=max_connections, **redis_server_settings["RLock"])
        self._redis = redis.Redis(connection_pool=self._connection_pool)

        for lock_key in self._redis.keys("lock__*"):
            self._redis.delete(lock_key)
        for lock_key in self._redis.keys("locksignal__*"):
            self._redis.delete(lock_key)

        # self._redis.flushdb()

    def get_connection(self):
        return self._redis


class RLock(object):
    def __init__(self, name, expire=3):
        self._client = RLockConnection().get_connection()
        self._expire = expire
        self._id = urandom(16)
        self._held = False
        self._name = "lock__"+name
        self._signal = "locksignal__"+name

    def reset(self):
        self._client.delete(self._name)
        self._client.delete(self._signal)

    def acquire(self, blocking=True, timeout=None):
        # from datetime import datetime

        # print "%s Acquire" % datetime.now()
        if self._held:
            raise AlreadyAcquired("Already acquired from this Lock instance.")

        busy = True
        blpop_timeout = timeout or self._expire or 0
        timed_out = False

        while busy:
            busy = not self._client.set(self._name, self._id, nx=True, ex=self._expire)
            # print "%s busy : " % datetime.now() + str(busy)
            if busy:
                if timed_out:
                    # print "%s timed_out, return False" % datetime.now()
                    return False
                elif blocking:
                    # print "%s timed_out #1" % datetime.now()
                    timed_out = not self._client.blpop(self._signal, blpop_timeout)
                    # print "%s timed_out #2 : %s" % (datetime.now(), str(timed_out))
                else:
                    # print "%s return False" % datetime.now()
                    return False
        self._held = True
        # print "%s return True" % datetime.now()
        return True

    def release(self, force=False):
        return self.__exit__(force=force)

    def __enter__(self):
        acquired = self.acquire(blocking=True)
        assert acquired, "Lock wasn't acquired, but blocking=True"
        return self

    def __exit__(self, exc_type=None, exc_value=None, traceback=None, force=False):
        if not (self._held or force):
            raise NotAcquired("This Lock instance didn't acquire the lock.")
        try:
            self._client.evalsha(UNLOCK_SCRIPT_HASH, 2, self._name, self._signal, self._id)
        except NoScriptError:
            self._client.eval(UNLOCK_SCRIPT, 2, self._name, self._signal, self._id)
        self._held = False
