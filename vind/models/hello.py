# -*- coding:utf-8 -*-
__author__ = 'ery'

import sys

sys.setdefaultencoding = "utf-8"
from datetime import datetime

from sqlalchemy import Column, Index, ForeignKey, Integer, Boolean, String, DateTime, TIMESTAMP, BLOB
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.sql import functions

from vind.tools import Base, SerializerMixin
from vind.models import Template


class HelloKv(Base, SerializerMixin, Template):
    __tablename__ = "hello_kv"

    key = Column(String(512), nullable=False)
    value = Column(LONGBLOB, nullable=False)
    is_valid = Column(Boolean, default=True, nullable=False)

    # author_idx = Column(Integer, \
    #                     ForeignKey("users.idx", onupdate="CASCADE", ondelete="NO ACTION"), nullable=False)

    created_at = Column(TIMESTAMP, server_default=functions.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=functions.current_timestamp(), \
                        server_onupdate=functions.current_timestamp(), nullable=True)

    idx_created_at = Index("idx_key", key)