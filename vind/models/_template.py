# -*- coding:utf-8 -*-
__author__ = 'ery'

import sys
sys.setdefaultencoding = "utf-8"

from sqlalchemy import Column, Index, Integer
from sqlalchemy.dialects.mysql import INTEGER, BIGINT, VARCHAR


class Template(object):
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8", "mysql_row_format": "Dynamic"}
    idx = Column(Integer, primary_key=True, autoincrement=True, nullable=False)


# class TSphinxSE(object):
#     __table_args__ = {"mysql_engine": "SPHINX", "mysql_connection": "unix:///var/run/searchd.sock"}
#     idx = Column(BIGINT(unsigned=True), nullable=False, primary_key=True)
#     weight = Column(INTEGER, nullable=False)
#     search_query = Column(VARCHAR(length=3072), nullable=False)
#     group_id = Column(INTEGER)
#
#     idx_search_query = Index("idx_search_query", search_query)

# """
#     CREATE TABLE sphinxse (
# 	idx BIGINT UNSIGNED NOT NULL,
# 	weight INTEGER NOT NULL,
# 	search_query VARCHAR(3072) NOT NULL,
# 	group_id INTEGER,
# 	INDEX(search_query)
#     )ENGINE=SPHINX CONNECTION='unix:///var/run/searchd.sock'
# """
# SELECT * FROM users_se WHERE search_token='@text 7d @text 8d;mode=extended;index=rt_test;ranker=none;';