# -*- coding:utf-8 -*-
__author__ = 'ery'

# print "[<-] %s" % (__name__,)

try:
    import ujson as json
except ImportError:
    import json
from functools import wraps
from flask import session, escape, jsonify


def check_range(factor, _min, _max):
    assert isinstance(factor, int) or isinstance(factor, float)
    if (factor >= _min) and (factor <= _max):
        return True
    else:
        return False


def check_req_data(req, essential_list=None, least_one_list=None):
    found_least_one_list = None

    try:
        data = json.loads(req.data)
    except Exception as e:
        return False, None, None

    if essential_list or least_one_list:

        data_keys = data.keys()
        if essential_list:
            assert isinstance(essential_list, (tuple, list))
            for entry in essential_list:
                if entry not in data_keys:
                    # print "1"
                    return False, None, None
        if least_one_list:
            assert isinstance(least_one_list, (tuple, list))
            found_least_one_list = []
            for entry in least_one_list:
                assert isinstance(entry, (str, tuple, list))
                if isinstance(entry, str):
                    # 하나의 문자열인경우
                    if entry in data_keys:
                        found_least_one_list.append(entry)
                else:
                    ie = []
                    for inner_entry in entry:
                        if inner_entry in data_keys:
                            ie.append(inner_entry)
                    if ie.__len__() == 0:
                        return False, None, None
                    found_least_one_list += ie
            if found_least_one_list.__len__() == 0:
                # print "2"
                return False, None, None

        return True, data, found_least_one_list
    else:
        # print "3"
        return True, data, None


# def check_req_data_ex(req, essential_list=None, least_one_list=None):
#     found_least_one_list = None
#
#     try:
#         data = json.loads(req.data)
#         data_keys = data.keys()
#     except Exception, e:
#         return False, None, None, None
#
#     if essential_list or least_one_list:
#         if essential_list:
#             assert isinstance(essential_list, list)
#             for entry in essential_list:
#                 if entry not in data_keys:
#                     # print "1"
#                     return False, None, None, data_keys
#         if least_one_list:
#             assert isinstance(least_one_list, list)
#             found_least_one_list = []
#             for entry in least_one_list:
#                 if entry in data_keys:
#                     found_least_one_list.append(entry)
#             if found_least_one_list.__len__() == 0:
#                 # print "2"
#                 return False, None, None, data_keys
#
#         return True, data, found_least_one_list, data_keys
#     else:
#         # print "3"
#         return True, data, None, data_keys

def userinfo_from_session():
    s = session
    user = s.get("user")
    if not user:
        return None
    return user


def parse_session():
    s = session
    user = s.get("user")
    if not user:
        return False, None, None
    is_admin = s.get("is_admin")

    idx = user["idx"]
    _id = user["id"]
    return is_admin, idx, _id


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = session.get("user")
        if session_token is None:
            return jsonify({"reason_text": "Require Login", "reason_code": 0}), 401
        escape(session)
        return f(*args, **kwargs)
    return decorated_function


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_admin = session.get("is_admin")
        if is_admin is None:
            return jsonify({"reason_text": "Require Login", "reason_code": 0}), 401
        else:
            if not is_admin:
                return jsonify({"reason_text": "Admin Only", "reason_code": 1}), 401
        escape(session)
        return f(*args, **kwargs)
    return decorated_function
