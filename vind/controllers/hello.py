# -*- coding:utf-8 -*-
from __future__ import print_function

__author__ = 'ery'

import logging
cl = logging.getLogger(__name__)

try:
    import ujson as json
except ImportError:
    import json

import zlib
import cPickle as pickle
from flask import abort, Blueprint, request, jsonify, session
from flask.ext.cache import Cache

from sqlalchemy import func, or_, and_, text

# from vind import cache
from vind.tools import DB
from vind.tools import pre_request_logging, after_request_logging, exec_teardown_request_handler, format_exception
from vind.tools import check_req_data, parse_session, admin_only, login_required
from vind.tools import zp, pz
from vind.models import HelloKv

app = hello_bp = Blueprint(__name__, "hello")
db = DB.get_session()

app.before_request(pre_request_logging)
app.after_request(after_request_logging)

teardown_request_handler = None
exec exec_teardown_request_handler
app.teardown_request(teardown_request_handler)

# ----- ----- header ----- -----

@app.route("/hello/set/<key>/<value>/", methods=["GET"])
def hello_set(key, value):
    hkv = db.query(HelloKv).filter_by(key=key).first()
    if not hkv:
        try:
            with db.begin_nested():
                hkv = HelloKv(key=key, value=zp(value))
                db.add(hkv)
        except Exception:
            print(format_exception())
            raise abort(500)
    else:
        try:
            # UPDATE HelloKv SET is_valid = False WHERE key = "key" and is_valid = True;
            with db.begin_nested():
                hkv = db.query(HelloKv)
                hkv = hkv.filter(HelloKv.key == key)
                hkv.update({HelloKv.value: zp(value)})
        except Exception:
            print(format_exception())
            raise abort(500)
    db.commit()

    # 원문
    # try:
    #     with db.begin_nested():
    #         hkv = HelloKv(key=key, value=zp(value))
    #         db.add(hkv)
    #     db.commit()
    # except Exception:
    #     print(format_exception())
    #     raise abort(500)

    return jsonify({"key": key, "value": value})


@app.route("/hello/set/", methods=["POST"])
def hello_post_set():
    is_ok, d, _ = check_req_data(request, essential_list=["key", "value"])
    if not is_ok:
        raise abort(400)
    key = d["key"]
    value = d["value"]

    hkv = db.query(HelloKv).filter_by(key=key).first()
    if not hkv:
        try:
            with db.begin_nested():
                hkv = HelloKv(key=key, value=zp(value))
                db.add(hkv)
        except Exception:
            print(format_exception())
            raise abort(500)
    else:
        try:
            # UPDATE HelloKv SET is_valid = False WHERE key = "key" and is_valid = True;
            with db.begin_nested():
                hkv = db.query(HelloKv)
                hkv = hkv.filter(HelloKv.key == key)
                hkv.update({HelloKv.value: zp(value)})
        except Exception:
            print(format_exception())
            raise abort(500)
    db.commit()

    # 원문
    # try:
    #     with db.begin_nested():
    #         hkv = HelloKv(key=key, value=zp(value))
    #         db.add(hkv)
    #     db.commit()
    # except Exception:
    #     print(format_exception())
    #     raise abort(500)

    return jsonify({"key": key, "value": value})


@app.route("/hello/get/<key>/", methods=["GET"])
def hello_get(key):
    hkv = db.query(HelloKv).filter_by(key=key, is_valid=True).first()

    # hkv = db.query(HelloKv)
    # hkv = hkv.filter(or_(HelloKv.key == key, HelloKv.key == 0))
    # hkv = hkv.filter(HelloKv.idx > 0)
    # hkv = hkv.group_by(HelloKv.key)
    # hkv = hkv.order_by(HelloKv.idx.desc())
    # hkv = hkv.all()

    # where key=key or key1=key1

    value = pz(hkv.value) if hkv else None
    return jsonify({key:value,})

@app.route("/hello/del/<key>/", methods=["GET"])
def hello_del(key):
    try:
        # UPDATE HelloKv SET is_valid = False WHERE key = "key" and is_valid = True;
        with db.begin_nested():
            hkv = db.query(HelloKv)
            hkv = hkv.filter(HelloKv.key == key)
            hkv = hkv.filter(HelloKv.is_valid == True)
            hkv.update({HelloKv.is_valid: False})
        db.commit()
    except Exception:
        print(format_exception())
        raise abort(500)

    return jsonify({"success": True})


@app.route("/hello/get/All/", methods=["GET"])
def hello_get_all():
    # print("## print test")
    hkv = db.query(HelloKv).filter_by(is_valid=True).all()

    # hkv = db.query(HelloKv)
    # hkv = hkv.filter(or_(HelloKv.key == key, HelloKv.key == 0))
    # hkv = hkv.filter(HelloKv.idx > 0)
    # hkv = hkv.group_by(HelloKv.key)
    # hkv = hkv.order_by(HelloKv.idx.desc())
    # hkv = hkv.all()

    # where key=key or key1=key1

    # value = pz(hkv.value) if hkv else None
    # return jsonify({"orders": [o.serialize(exclude=["idx_key"]) for o in orders]}), 200
    return jsonify({"result" : [{"key" : i.key , "value" : pz(i.value)} for i in hkv] }), 200

# map(lamda) 사용 법
# [ i for i in some_list ] 란 배열의 값들을 다 곱하기 2 하고 싶다
# [ i*2 for i in some_list ] 보다
# map(lambda x: x*2, some_list) 이게 속도가 더 빠르다.
