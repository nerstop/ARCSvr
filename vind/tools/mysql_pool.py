# -*- coding:utf-8 -*-
__author__ = 'ery'

import sys

reload(sys)
sys.setdefaultencoding("utf-8")


import logging

import mysql.connector as mc
from vind.tools import Singleton
from vind.config import mysql_connector_connect_strings


from vind.tools import IConnectionPool
from mysql.connector.connection import MySQLConnection


class SphinxConnectionPool(IConnectionPool):
    __metaclass__ = Singleton

    def __init__(self, size=8, keepalive=30, ):
        self.logger = None
        self._ld = None
        self._li = None
        self._lw = None
        self._le = None
        self._lc = None
        super(SphinxConnectionPool, self).__init__(logger_name="connection_pool.SphinxQL",
                                                   logger_level=logging.INFO, ensure_unique=True,
                                                   size=size, keepalive=keepalive, exc_classes=(mc.Error,))
        self._ld("before forking")

    def _new_connection(self):
        class SphinxMySQLConnection(MySQLConnection):
            def connect(self, **kwargs):
                if len(kwargs) > 0:
                    self.config(**kwargs)

                self.disconnect()
                self._open_connection()
        try:
            return SphinxMySQLConnection(**mysql_connector_connect_strings["Sphinx"])
        except mc.Error as err:
            self._le("SphinxConnectionPool._new_connection, mysql.connector.Error=%s" % (str(err),))
            return None
        except Exception as err:
            self._le("SphinxConnectionPool._new_connection, Exception=%s" % (str(err),))
            return None

    def _keepalive(self, cnx):
        cnx.ping(reconnect=True, attempts=2 ** 16, delay=0.25)

    # def _reset_connection(self, cnx):
    #     """exception handling required in this function"""
    #     try:
    #         if cnx and hasattr(cnx, "rollback"):
    #             cnx.rollback()
    #     except Exception as err:
    #         self._le("OVERLOADED _reset_connection, err=%s" % (str(err),))

    def _dispose_connection(self, cnx):
        """exception handling required in this function"""
        try:
            if cnx and hasattr(cnx, "rollback"):
                cnx.rollback()
            if cnx and hasattr(cnx, "close"):
                cnx.close()
        except Exception as err:
            # 로깅대신 박아놓음 임시로
            self._le("OVERLOADED _dispose_connection, err=%s" % (str(err),))
        finally:
            del cnx


class MySQLSettingConnectionPool(IConnectionPool):
    __metaclass__ = Singleton

    def __init__(self, size=8, keepalive=30, ):
        self.logger = None
        self._ld = None
        self._li = None
        self._lw = None
        self._le = None
        self._lc = None
        super(MySQLSettingConnectionPool, self).__init__(logger_name="connection_pool.MySQLSetting",
                                                         logger_level=logging.INFO, ensure_unique=True,
                                                         size=size, keepalive=keepalive, exc_classes=(mc.Error,))
        self._ld("before forking")

    def _new_connection(self):
        try:
            return mc.connect(**mysql_connector_connect_strings["Setting"])
        except mc.Error as err:
            self._le("MySQLSettingConnectionPool._new_connection, mysql.connector.Error=%s" % (str(err),))
            return None
        except Exception as err:
            self._le("MySQLSettingConnectionPool._new_connection, Exception=%s" % (str(err),))
            return None

    def _keepalive(self, cnx):
        cnx.ping(reconnect=True, attempts=2 ** 16, delay=0.25)

    # def _reset_connection(self, cnx):
    #     """exception handling required in this function"""
    #     try:
    #         if cnx and hasattr(cnx, "rollback"):
    #             cnx.rollback()
    #     except Exception as err:
    #         self._le("OVERLOADED _reset_connection, err=%s" % (str(err),))

    def _dispose_connection(self, cnx):
        """exception handling required in this function"""
        try:
            if cnx and hasattr(cnx, "rollback"):
                cnx.rollback()
            if cnx and hasattr(cnx, "close"):
                cnx.close()
        except Exception as err:
            # 로깅대신 박아놓음 임시로
            self._le("OVERLOADED _dispose_connection, err=%s" % (str(err),))
        finally:
            del cnx


class MySQLConnectionPool(IConnectionPool):
    __metaclass__ = Singleton

    def __init__(self, size=8, keepalive=30, ):
        self.logger = None
        self._ld = None
        self._li = None
        self._lw = None
        self._le = None
        self._lc = None
        super(MySQLConnectionPool, self).__init__(logger_name="connection_pool.MySQL",
                                                  logger_level=logging.INFO, ensure_unique=True,
                                                  size=size, keepalive=keepalive, exc_classes=(mc.Error,))
        self._ld("before forking")

    def _new_connection(self):
        try:
            return mc.connect(**mysql_connector_connect_strings["Sphinx"])
        except mc.Error as err:
            self._le("MySQLConnectionPool._new_connection, mysql.connector.Error=%s" % (str(err),))
            return None
        except Exception as err:
            self._le("MySQLConnectionPool._new_connection, Exception=%s" % (str(err),))
            return None

    def _keepalive(self, cnx):
        cnx.ping(reconnect=True, attempts=2 ** 16, delay=0.25)

    def _reset_connection(self, cnx):
        """exception handling required in this function"""
        try:
            if cnx and hasattr(cnx, "rollback"):
                cnx.rollback()
        except Exception as err:
            print(err)

    def _dispose_connection(self, cnx):
        """exception handling required in this function"""
        try:
            if cnx and hasattr(cnx, "rollback"):
                cnx.rollback()
            if cnx and hasattr(cnx, "close"):
                cnx.close()
        except Exception as err:
            # 로깅대신 박아놓음 임시로
            print(err)
        finally:
            del cnx
