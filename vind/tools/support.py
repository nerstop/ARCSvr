# -*- coding:utf-8 -*-
__author__ = 'ery'

try:
    import ujson as json
except ImportError:
    import json

import zlib, cPickle as pickle
from datetime import datetime, timedelta

from sqlalchemy import func, or_, and_, text
from vind.tools import DB, GS, RLock, SPHRT
from vind.models import *


def sub_calculate_point_group_by_type(users_idx, db_session):
    ps = db_session.query(Point.type, func.sum(Point.how_much).label("sum")).filter_by(users_idx=users_idx).\
        group_by(Point.type).all()
    normal_decrease = 0
    normal_increase = 0
    special_decrease = 0
    special_increase = 0
    if ps.__len__() > 0:
        for p in ps:
            if p.type == 1:
                normal_decrease += p.sum
            elif p.type == 2:
                normal_increase += p.sum
            elif p.type == 3:
                special_decrease += p.sum
            elif p.type == 4:
                special_increase += p.sum
    return normal_decrease, normal_increase, special_decrease, special_increase


def query_calculated_point_of_user(users_idx, db_session, use_lock=False):
    try:
        if use_lock:
            with RLock("__vind.point.%d" % (users_idx,), 3):
                ps = db_session.query(Point.type, func.sum(Point.how_much).label("sum")).\
                    filter_by(users_idx=users_idx).group_by(Point.type).all()
        else:
            ps = db_session.query(Point.type, func.sum(Point.how_much).label("sum")).\
                filter_by(users_idx=users_idx).group_by(Point.type).all()
        if ps.__len__() > 0:
            normal_decrease = 0
            normal_increase = 0
            special_decrease = 0
            special_increase = 0
            for p in ps:
                if p.type == 1:
                    normal_decrease += p.sum
                elif p.type == 2:
                    normal_increase += p.sum
                elif p.type == 3:
                    special_decrease += p.sum
                elif p.type == 4:
                    special_increase += p.sum
            usable_point = (special_increase - special_decrease) + (normal_increase - normal_decrease)
            if special_increase - special_decrease < 0:
                print "#1"
                withdrawable_point = usable_point
            else:
                print "#2"
                withdrawable_point = normal_increase - normal_decrease
            if withdrawable_point < 0:
                withdrawable_point = 0

            return True, usable_point, withdrawable_point
        else:
            return False, 0, 0
    except Exception as e:
        print("_query_calculated_point_of_user : %s" % (unicode(e),))
        return False, 0, 0
    finally:
        pass
