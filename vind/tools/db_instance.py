# -*- coding:utf-8 -*-
__author__ = 'ery'

import sys, os
import logging
from time import time as stime
import mysql.connector

from sqlalchemy import create_engine, event, select, dialects
from sqlalchemy.util import safe_reraise
from sqlalchemy.pool import Pool, QueuePool
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import TimeoutError, DisconnectionError, DBAPIError
from sqlalchemy.ext.declarative import declarative_base

from vind.tools import Singleton
# from vind.tools import GS
from vind.config import mysql_connector_connect_strings, \
    sqlalchemy_engine_settings, sqlalchemy_sessionmaker_settings, sqlalchemy_queuepool_settings

# sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
pool_logger = logging.getLogger("sqlalchemy.pool")
# pool_logger.setLevel(logging.DEBUG)
gqpool_logger = logging.getLogger("sqlalchemy.pool.GQueuePool")
# gqpool_logger.setLevel(logging.DEBUG)

from gevent import spawn_later
from gevent.lock import RLock as GRLock
from gevent.event import Event as GEvent
from gevent.queue import Full, Empty, PriorityQueue as GPQueue


# class GQueuePool(Pool):
#     def __init__(self, creator, recycle=-1, echo=None, use_threadlocal=False, logging_name=None, reset_on_return=True,
#                  listeners=None, events=None, _dispatch=None, _dialect=None, max_connections=None,
#                  reserve_connections=None, connection_idle_timeout=5):
#         super(GQueuePool, self).__init__(
#             creator, recycle=recycle, echo=echo, use_threadlocal=use_threadlocal, logging_name=logging_name,
#             reset_on_return=reset_on_return,
#             listeners=listeners, events=events, _dispatch=_dispatch, _dialect=_dialect)
#
#         self.max_connections = max_connections or 8
#         self.reserve_connections = reserve_connections or 2
#         self.connection_idle_timeout = connection_idle_timeout
#
#         self._lock = GRLock()
#         self._available = GPQueue()  # list()
#         self._inuse = list()
#         self._timeouter = spawn_later(self.connection_idle_timeout, self._timeout)
#         self._is_not_empty = GEvent()
#         gqpool_logger.debug("Pool created")
#
#     def recreate(self):
#         gqpool_logger.debug("Pool recreating")
#         return self.__class__(
#             self._creator, recycle=self._recycle, echo=self.echo, use_threadlocal=self._use_threadlocal,
#             logging_name=self._orig_logging_name, reset_on_return=self._reset_on_return, _dispatch=self.dispatch,
#             _dialect=self._dialect, max_connections=self.max_connections, reserve_connections=self.reserve_connections,
#             connection_idle_timeout=self.connection_idle_timeout)
#
#     def dispose(self):
#         gqpool_logger.error("### 1")
#         with self._lock:
#             gqpool_logger.error("### 1-1")
#             while not self._available.empty():
#                 try:
#                     t, connection = self._available.get(block=True, timeout=3)
#                 except Empty:
#                     gqpool_logger.error("GPQueue raised timeout in self.dispose")
#                     continue
#
#                 try:
#                     connection.close()
#                 except Exception:
#                     pass
#         gqpool_logger.debug("Pool disposed. %s", self.status())
#
#     def _timeout(self):
#         try:
#             gqpool_logger.error("### 2")
#             with self._lock:
#                 gqpool_logger.error("### 2-1")
#                 while not self._available.empty() and \
#                                         self._available.qsize() + len(self._inuse) > self.reserve_connections:
#                     gqpool_logger.error("### 2-2")
#                     t, connection = self._available.get(block=True, timeout=3)
#                     gqpool_logger.error("### 2-3")
#                     if t + self.connection_idle_timeout < stime():
#                         try:
#                             gqpool_logger.error("### 2-4")
#                             connection.close()
#                             gqpool_logger.error("### 2-5")
#                         except Exception:
#                             gqpool_logger.error("### 2-6")
#                             pass
#                     else:
#                         gqpool_logger.error("### 2-7")
#                         self._available.put((t, connection))
#                         gqpool_logger.error("### 2-8")
#                         break
#                     gqpool_logger.debug("closing timed out connection after %0.2f seconds (%s available, %s in use)",
#                                         stime() - t, len(self._available), len(self._inuse))
#         except Empty:
#             gqpool_logger.error("GPQueue raised timeout in self._timeout")
#         finally:
#             gqpool_logger.error("### 2-9")
#             self._timeouter = spawn_later(self.connection_idle_timeout, self._timeout)
#
#     def _do_get(self):
#         while True:
#             try:
#                 gqpool_logger.error("### 3")
#                 with self._lock:
#                     gqpool_logger.error("### 3-1")
#                     if not self._available.empty():
#                         t, connection = self._available.get(block=True, timeout=3)
#                         gqpool_logger.debug("pop connection (%s available, %s in use)", \
#                                             self._available.qsize(), len(self._inuse))
#                     else:
#                         if self.max_connections is not None and len(self._inuse) >= self.max_connections:
#                             self._is_not_empty.clear()
#                             raise Empty("max connections of %s reached" % self.max_connections)
#                         connection = self._create_connection()
#                         gqpool_logger.debug("new connection (%s available, %s in use)", self._available.qsize(),
#                                             len(self._inuse) + 1)
#                     self._inuse.append(connection)
#             except Empty:
#                 gqpool_logger.error("pool empty. waiting for available slot (%s available, %s in use)",
#                                     self._available.qsize(), len(self._inuse))
#                 self._is_not_empty.wait(timeout=3)
#                 gqpool_logger.error("### 3-2")
#             else:
#                 return connection
#
#     def _do_return_conn(self, connection):
#         gqpool_logger.error("### 4")
#         with self._lock:
#             gqpool_logger.error("### 4-1")
#             gqpool_logger.debug('release connection (%s available, %s in use)', self._available.qsize(), len(self._inuse))
#             self._inuse.remove(connection)
#             self._available.put_nowait((stime(), connection))
#             gqpool_logger.error("### 4-2, before signal")
#             self._is_not_empty.set()
#             gqpool_logger.error("### 4-3, after signal")
#
#     def status(self):
#         return "Pool size: %d  Connections in pool: %d Current Checked out connections: %d" % \
#                (self.max_connections, self._available.qsize(), len(self._inuse))


# 현재 이런 문제가 있다.
# 1. 어떤 이유로든 에러가 나서 반환되지 않은경우, 갯수 자체는 그대로 차지하지만 실제로 풀로는 영원히 돌아오지 않으므로
#   들어올 리가 없는 커넥션을 대기하다가 타임아웃이 난다.
# -> 해결책 1 : _go_get 을 수정하여 해당 함수를 호출한 커넥션에서 에러가 났는지를 판단하고 재회수 하던지 새로 만들던지 한다.
# -> 해결책 2 : _go_get 에서 커넥션을 꺼내줄때, 해당 커넥션을 꺼낸 시간을 기록하고 지정된 시간동안 반환되지 않으면 파기하고 새로 만든다.
#              당연히 별개의 스레드로 동작해야 한다.
# 2. 당연히 문제가 없을 줄 알고 꺼낸 커넥션이 문제가 있다.
# -> 해결책 1 : _do_get 에서 소켓 관련 에러를 감지하면, 해당 커넥션을 파기하고 재생성한다
# -> 해결책 2 : 별도의 스레드를 만들어서, 커넥션들의 신선도를 계속 체크하여 유지 관리한다.


class GQueuePool(Pool):
    def __init__(self, creator, pool_size=5, max_overflow=10, timeout=30, **kw):
        Pool.__init__(self, creator, **kw)
        self._pool = GPQueue(pool_size + max_overflow)
        self._overflow = 0 - pool_size
        self._max_overflow = max_overflow
        self._timeout = timeout
        self._overflow_lock = GRLock()
        gqpool_logger.debug("Pool created")

    def _do_return_conn(self, conn):
        try:
            self._pool.put((stime(), conn), False)
        except Full:
            try:
                conn.close()
            finally:
                self._dec_overflow()

    def _do_get(self):
        use_overflow = self._max_overflow > -1

        try:
            wait = use_overflow and self._overflow >= self._max_overflow
            return self._pool.get(block=wait, timeout=self._timeout)[1]
        except Empty:
            if use_overflow and self._overflow >= self._max_overflow:
                if not wait:
                    return self._do_get()
                else:
                    raise TimeoutError(
                        "GQueuePool limit of size %d overflow %d reached, "
                        "connection timed out, timeout %d" %
                        (self.size(), self.overflow(), self._timeout))

            if self._inc_overflow():
                try:
                    return self._create_connection()
                except:
                    with safe_reraise():
                        self._dec_overflow()
            else:
                return self._do_get()

    def _inc_overflow(self):
        if self._max_overflow == -1:
            self._overflow += 1
            return True
        with self._overflow_lock:
            if self._overflow < self._max_overflow:
                self._overflow += 1
                return True
            else:
                return False

    def _dec_overflow(self):
        if self._max_overflow == -1:
            self._overflow -= 1
            return True
        with self._overflow_lock:
            self._overflow -= 1
            return True

    def recreate(self):
        gqpool_logger.debug("Pool recreating")
        return self.__class__(self._creator, pool_size=self._pool.maxsize,
                              max_overflow=self._max_overflow,
                              timeout=self._timeout,
                              recycle=self._recycle, echo=self.echo,
                              logging_name=self._orig_logging_name,
                              use_threadlocal=self._use_threadlocal,
                              reset_on_return=self._reset_on_return,
                              _dispatch=self.dispatch,
                              _dialect=self._dialect)

    def dispose(self):
        while True:
            try:
                conn = self._pool.get(False)[1]
                conn.close()
            except Empty:
                break

        self._overflow = 0 - self.size()
        gqpool_logger.debug("Pool disposed. %s", self.status())

    def status(self):
        return "Pool size: %d  Connections in pool: %d " \
               "Current Overflow: %d Current Checked out " \
               "connections: %d" % (self.size(),
                                    self.checkedin(),
                                    self.overflow(),
                                    self.checkedout())

    def size(self):
        return self._pool.maxsize

    def checkedin(self):
        return self._pool.qsize()

    def overflow(self):
        return self._overflow

    def checkedout(self):
        return self._pool.maxsize - self._pool.qsize() + self._overflow


class DbInstance(object):
    __metaclass__ = Singleton

    def __init__(self):
        # self._mode = GS.getd("OPERATION_MODE")
        self._mode = "development"
        if not ((self._mode == "development") or (self._mode == "production")):
            raise ValueError("Invalid value on OPERATION_MODE : %s" % (self._mode,))
        # self._connector = GS.getd("SQLALCHEMY_CONNECTOR")
        self._connector = "mysql.connector"
        if not ((self._connector == "MySQLdb") or (self._connector == "mysql.connector")):
            raise ValueError("Invalid value on SQLALCHEMY_CONNECTOR : %s" % (self._connector,))

        self._pool = None
        self._engine = None

        self._gevent_already_patched = False

    def _getconn(self):
        pool_logger.debug("[I] _getconn")
        c = mysql.connector.connect(**(mysql_connector_connect_strings["Common"]))
        pool_logger.debug("[O] _getconn")
        return c

    def _create_engine(self):
        if "SQLALCHEMY_SILENT" in os.environ:
            sqlalchemy_logger = logging.getLogger("sqlalchemy")
            sqlalchemy_logger.info("`sqlalchemy` logger level elevated to `Warning`")
            sqlalchemy_logger.setLevel(logging.WARNING)
        pool_logger.debug("[I] _create_engine")
        dialects.registry.register("mysqlconnector", "sqlalchemy_gevent", "MysqlMysqlconnectorDialect")
        e = create_engine("mysqlconnector://", pool=self.get_pool(), **(sqlalchemy_engine_settings[self._mode]))
        pool_logger.debug("[O] _create_engine")
        return e

    def get_engine(self):
        pool_logger.debug("[I] get_engine")
        if not self._engine:
            pool_logger.debug("Engine Created")
            self._engine = self._create_engine()
        pool_logger.debug("[O] get_engine")
        return self._engine

    def get_pool(self):
        pool_logger.debug("[I] get_pool")
        if not self._pool:
            self._pool = GQueuePool(self._getconn, **(sqlalchemy_queuepool_settings[self._mode]))
            # pool_logger.debug("GQueuePool Created")
            # self._pool = QueuePool(self._getconn, **(sqlalchemy_queuepool_settings[self._mode]))
            pool_logger.debug("GQueuePool Created")
            # gevent patch
            # https://github.com/kljensen/async-flask-sqlalchemy-example/blob/master/server.py
            if (not self._gevent_already_patched) and sys.modules.keys().count("gevent") > 0:
                pool_logger.debug("`_user_threadlocal = True` for Gevent")
                self._pool._use_threadlocal = True
                self._gevent_already_patched = True
        pool_logger.debug("[O] get_pool")
        return self._pool

    def get_session(self):
        pool_logger.debug("[I] get_session")
        ss = scoped_session(session_factory=sessionmaker(bind=self.get_engine(), \
                                                         **(sqlalchemy_sessionmaker_settings["Common"])))
        pool_logger.debug("[O] get_session")
        return ss


DB = DbInstance()

Base = declarative_base()
Base.query = DB.get_session().query_property()


# 이건 sqlalchemy 가 자동으로 처리해주는부분인것 같다.
# @event.listens_for(DB.get_engine(), "engine_connect")
# def event_engine_check_connection(connection, branch):
#     if branch:
#         return
#     try:
#         connection.scalar(select([1]))
#     except DBAPIError as e:
#         if e.connection_invalidated:
#             connection.scalar(select([1]))
#         else:
#             raise

# 디비가 리붓되거나 할때 자동으로 복귀시키기 위해 필요함.
# 두세번 재시도하도록 짜는게 나을지도
@event.listens_for(DB.get_pool(), "checkout")
def event_pool_checkout(dbapi_con, connection_record, connection_proxy):
    try:
        pool_logger.debug("HOOK : event_pool_checkout attempt ping")
        dbapi_con.ping()
        pool_logger.debug("HOOK : event_pool_checkout ping success")
    except Exception as e:
        pool_logger.critical("HOOK : event_pool_checkout ping failed, %s" % (str(e),))
        raise DisconnectionError()


# http://docs.sqlalchemy.org/en/latest/core/events.html
if "SQLALCHEMY_SILENT" not in os.environ:  # and (not GS.is_production()):
    @event.listens_for(DB.get_pool(), "checkin")
    def event_pool_checkin(dbapi_con, connection_record):
        pool_logger.debug("HOOK : event_pool_checkin")


    @event.listens_for(DB.get_pool(), "connect")
    def event_pool_connect(dbapi_con, connection_record):
        pool_logger.debug("HOOK : event_pool_connect")


    @event.listens_for(DB.get_pool(), "first_connect")
    def event_pool_first_connect(dbapi_con, connection_record):
        pool_logger.debug("HOOK : event_pool_first_connect")


    @event.listens_for(DB.get_pool(), "invalidate")
    def event_pool_invalidate(dbapi_con, connection_record, connection_proxy):
        pool_logger.debug("HOOK : event_pool_invalidate")


    @event.listens_for(DB.get_pool(), "reset")
    def event_pool_reset(dbapi_con, connection_record):
        pool_logger.debug("HOOK : event_pool_reset")


    @event.listens_for(DB.get_pool(), "soft_invalidate")
    def event_pool_soft_invalidate(dbapi_con, connection_record, connection_proxy):
        pool_logger.debug("HOOK : event_pool_soft_invalidate")
