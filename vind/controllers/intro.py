# -*- coding:utf-8 -*-
from __future__ import print_function

__author__ = 'nerstop'

import logging
cl = logging.getLogger(__name__)

try:
    import ujson as json
except ImportError:
    import json

import zlib
import cPickle as pickle
from hashlib import sha256
from flask import abort, Blueprint, request, jsonify, session
from flask.ext.cache import Cache

from sqlalchemy import func, or_, and_, text

# from vind import cache
from vind.tools import DB, RLock
from vind.tools import pre_request_logging, after_request_logging, exec_teardown_request_handler, format_exception
from vind.tools import check_req_data, parse_session, admin_only, login_required
from vind.config import f401
from vind.tools import zp, pz
from vind.models import UserInfo, UserProfile

app = intro_bp = Blueprint(__name__, "intro")
db = DB.get_session()

app.before_request(pre_request_logging)
app.after_request(after_request_logging)

teardown_request_handler = None
exec exec_teardown_request_handler
app.teardown_request(teardown_request_handler)

# ----- ----- header ----- -----

@app.route("/intro/signin/", methods=["POST"])
#def login(force=False):
def login():
    is_ok, d, _ = check_req_data(request, essential_list=["userId"])
    if not is_ok:
        raise abort(400)

    # if force:
    #     user = db.query(UserInfo).filter_by(userId=d["userId"], is_active=True).first()
    # else:
    if "userPw" not in d:
        raise abort(400)
    user = db.query(UserInfo).filter_by(userId=d["userId"], userPw=sha256(d["userPw"]).hexdigest(), is_active=True).first()

    if not user:
        return jsonify(f401[3]), 401
    uidx = user.idx
    # with RLock("__vind.users.%d" % (uidx,), 3):
    user_pf = db.query(UserProfile).filter_by(idx=user.idx).first()

    if not user_pf:
        # this can't be !!
        raise abort(500)

    session["user"] = {}
    session["user"]["idx"] = uidx
    session["user"]["userId"] = user.userId
    session["user"]["name"] = user.name
    session["user"]["bDay"] = user.bDay
    session["user"]["sex"] = user.sex
    session["user"]["phone"] = user.phone
    session["user"]["photo"] = user.photo
    session["user"]["point"] = user.point
    session["user"]["flag"] = user.flag
    session["user"]["device_type"] = user.device_type
    session["user_profile"] = user_pf.serialize()
    session["is_active"] = user.is_active

    result = {"user": user.serialize(exclude=["userPw"]), "user_profile": user_pf.serialize()}

    return jsonify(result), 200


@app.route("/intro/signup/", methods=["POST"])
def join_new_users():
    essential_args = ["userId", "userPw", "name", "bDay", "sex", "phone",
                      "flag", "weight", "height","BMI", "device_type"]
    # flag 가 0번이면 stdid 와 major는 필수가 됨.!
    # goalWeight은 선택이지만~있음 좋겠지

    is_ok, d, _ = check_req_data(request, essential_list=essential_args)
    if not is_ok:
        # print str(is_ok), str(d), str(l)
        raise abort(400)

    check_user = db.query(UserInfo).filter(UserInfo.userId == d["userId"]).first()
    if check_user:
        if check_user.id == d["userId"]:
            return jsonify(f401[110]), 401 # 아이디가 겹침
        else:
            return jsonify(f401[200]), 401 # 정상

    import hashlib
    userPw_sha256 = hashlib.sha256(d["userPw"]).hexdigest()


    # 나중에 디바이스 아이디를 추가해야될경우
    if d["device_type"] == 0:
        # Android
        pass
    elif d["device_type"] == 1:
        # iOS
        pass
    else:
        # Abnormal
        pass


    try:
        with db.begin_nested():
            user = UserInfo(userId=d["userId"],
                            userPw=userPw_sha256,
                            name=d["name"],
                            stdId=d["stdId"] if d["flag"] == 0 else "",
                            major=d["major"] if d["flag"] == 0 else "",
                            bDay=d["bDay"],
                            sex=d["sex"],
                            phone=d["phone"],
                            flag=d["flag"],
                            )
            db.add(user)
            db.flush()
            user_pf = UserProfile(idx=user.idx,
                                  weight=d["weight"],
                                  goalWeight=d["goalWeight"] if d["goalWeight"] > 0 else 0,
                                  height=d["height"],
                                  BMI=d["BMI"],
                                  )
            db.add(user_pf)
            # 300 : 회원가입시의 포인트 증정
            # point_default_for_new_user = Point(users_idx=user.idx, type=4, reason=300, how_much=point_initial)
            # db.add(point_default_for_new_user)
            # ubl = UserBehaviorLog(users_idx=user.idx, behavior=0)
            # db.add(ubl)

    except Exception:
        print(format_exception())
        print("EXCEPTION : /users/signup/ #2")
        raise abort(500)

    db.commit()


    # stdId, major is nullable true
    # General user is haven't stdId, major
    # photo is default image for new users
    # point is initialize value 0
    # return jsonify({"result": "success"})
    return jsonify({"userInfo": user.serialize(exclude=["userPw"]), "user_Profile": user_pf.serialize()}), 200

