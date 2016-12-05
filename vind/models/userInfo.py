# -*- coding:utf-8 -*-
__author__ = 'nerstop'

import sys

sys.setdefaultencoding = "utf-8"
from datetime import datetime

from sqlalchemy import Column, Index, ForeignKey, Integer, Boolean, String, DateTime, TIMESTAMP, BLOB
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.sql import functions

from vind.tools import Base, SerializerMixin
from vind.models import Template


class UserInfo(Base, SerializerMixin, Template):
    __tablename__ = "userInfo"

    userId = Column(String(16), unique=True, nullable = False)
    userPw = Column(String(64), nullable = False)
    name = Column(String(30), nullable = False)
    stdId = Column(String(15), nullable = True)
    major = Column(String(20), nullable = True)
    bDay = Column(String(8), nullable = False)
    sex = Column(Boolean, nullable = False)
    phone = Column(String(10), nullable = False)
    photo = Column(String(128), default = "default", nullable = False)
    point = Column(Integer, default = 0 , nullable = False)
    # 0 : Student
    # 1 : General
    # 2 : Admin
    flag = Column(Integer, nullable = False)
    # 0 : Android
    # 1 : iOS
    device_type = Column(Integer, default=0, nullable=False)
    # 계정 활성화 상태(활동/탈퇴)
    is_active = Column(Boolean, default=True, nullable=False)

    # author_idx = Column(Integer, \
    #                     ForeignKey("users.idx", onupdate="CASCADE", ondelete="NO ACTION"), nullable=False)

    created_at = Column(TIMESTAMP, server_default=functions.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=functions.current_timestamp(), \
                        server_onupdate=functions.current_timestamp(), nullable=True)

    idx_id = Index("idx_id", userId)

class UserProfile(Base, SerializerMixin):
    __table_args__ = {"mysql_engine": "InnoDB", "mysql_charset": "utf8"}
    __tablename__ = "userProfile"

    idx = Column(Integer, ForeignKey("userInfo.idx", ondelete="CASCADE", onupdate="CASCADE"),
                 primary_key=True, nullable=False)
    weight = Column(Integer, nullable=False)
    # 목표체중이 없을수도 있..지?
    goalWeight = Column(Integer, nullable=True)
    height = Column(Integer, nullable=False)
    BMI = Column(Integer, nullable=False)

    updated_at = Column(TIMESTAMP, server_default=functions.current_timestamp(), \
                         server_onupdate=functions.current_timestamp(), nullable=True)


    # weight // pound
    # goalWeight
    # height // ft / in
    # BMI -> 계산


    # address_main_idx = Column(Integer, ForeignKey("address.idx", ondelete="NO ACTION", onupdate="CASCADE"), \
    #                           nullable=False)
    # address_detail = Column(String(128), nullable=False)
    # address = Column(String(256), nullable=False)
    # # resident_registration = Column(String(16), nullable=True)
    # # business_license = Column(String(16), nullable=True)
    # # state (휴폐업상태) : 0: 등록되지 않은 사업자번호, 1: 사업중, 2: 폐업, 3: 휴업
    # # business_state = Column(TINYINT, default=0, nullable=False)
    # # type (사업유형) : 0: 알수없음, 검사되지않음, 1: 일반과세자, 2: 면세과세자, 3: 간이과세자, 4: 비영리법인, 국가기관
    # # business_type = Column(TINYINT, default=0, nullable=False)
    # regular_to = Column(DateTime, nullable=True)
    # email = Column(String(64), nullable=False)
    # bank_name = Column(String(32), nullable=True)
    # bank_number = Column(String(64), nullable=True)
    # floor_min = Column(Integer, nullable=False)
    # floor_max = Column(Integer, nullable=False)
    # car_num = Column(String(10), nullable=True)
    # warning_count = Column(Integer, default=0, nullable=False)
    # comment = Column(String(256), nullable=True)
    # withdraw_scheduled = Column(DateTime, default=None, nullable=True)
    # updated_at = Column(TIMESTAMP, server_default=functions.current_timestamp(), \
    #                     server_onupdate=functions.current_timestamp(), nullable=True)



        # ---profile---
# idx : pk
# userIdx : uk, fk
# weight // pound
# goalWeight
# height // ft / in
# BMI -> 계산