# -*- coding:utf-8 -*-
__author__ = 'ery'


from celery import Task, signals

from sqlalchemy import func, or_, and_, text
from vind.tools import DB, RLock, SPHRT, GS
# from vind.models import *
from vind.utils.async import capp, BaseTask, NoResultTask
from vind.config import push_message_codes


@capp.task(base=NoResultTask, name="vind.utils.async.functions.android_push")
def android_push(uuids, message):
    print "vind.utils.async.message.android_push"

    if not uuids:
        return False

    from gcm import GCM

    g = GCM("AIzaSyAheYj04o3dgHhG8MrN5NGQKY4HT8NhzKc")

    try:
        if isinstance(uuids, (list, tuple, set)):
            g.json_request(registration_ids=uuids, data=message)
        elif isinstance(uuids, str):
            g.plaintext_request(registration_id=uuids, data=message)
    except Exception, e:
        print e
        return False
    return True


@capp.task(base=NoResultTask, name="vind.utils.async.functions.ios_push")
def ios_push(uuids, message):
    return True


@capp.task(base=NoResultTask, name="vind.utils.async.functions.mpush")
def message_mpush(ids, code=None, message=None):
    print "vind.utils.async.message.mpush"
    print ids, message, code

    if not isinstance(ids, (str, set, list, tuple)):
        return False

    if (not code) and (not message):
        print "B #1"
        return False
    else:
        if code:
            if code not in push_message_codes:
                print "B #2"
                return False
            msg = push_message_codes[code]
        elif message:
            msg = unicode(message)
        else:
            print "vind.utils.async.message.ios_push : Exception #1"
            return False

    if isinstance(ids, str):
        # 1개만 보내는 경우
        uuid = ids[3:]
        if int(ids[:2]) == 0:
            # Android
            android_push.apply_async(args=((uuid,), msg))
        elif int(ids[:2]) == 1:
            # iOS
            ios_push.apply_async(args=((uuid,), msg))
    else:
        # list, set 등으로 다수인 경우
        if ids.__len__() == 0:
            print "B #3"
            return False

        if isinstance(ids, set):
            ids = tuple(ids)

        uuid_android = []
        uuid_ios = []

        for uuid in ids:
            if int(uuid[:2]) == 0:
                uuid_android.append(uuid[3:])
            elif int(uuid[:2]) == 1:
                uuid_ios.append(uuid[3:])
            else:
                print "Invalid uuid form : %s" % (uuid,)

        chunk_size = GS.getd("VAR_CELERY_PUSH_CHUNK_SIZE")
        for i in xrange((uuid_android.__len__() / chunk_size) + 1):
            android_push.apply_async(args=(uuid_android[i * chunk_size: (i + 1) * chunk_size], msg))
        for i in xrange((uuid_ios.__len__() / chunk_size) + 1):
            ios_push.apply_async(args=(uuid_ios[i * chunk_size: (i + 1) * chunk_size], msg))

    return True


# @capp.task(base=BaseTask, name="vind.utils.async.functions.check_bussiness_license")
# def check_bussiness_license(users_idx):
#     pass


# @capp.task(base=BaseTask, name="vind.utils.async.functions.withdraw_users")
# def withdraw_users():
#     pass


# @capp.task(base=BaseTask, name="vind.utils.async.functions.address_added")
# def address_added(addr_idx):
#     pass
#
#
# @capp.task(base=BaseTask, name="vind.utils.async.functions.address_deleted")
# def address_deleted(addr_idx):
#     pass


@capp.task(base=BaseTask, name="vind.utils.async.functions.address_rebuild")
def address_rebuild():
    pass


# @capp.task(base=BaseTask, name="vind.utils.async.functions.notify_new_order")
# def notify_new_order(orders_idx):
#     pass


# @capp.task(base=BaseTask, name="vind.utils.async.functions.sph_rt_rebuild_users")
# def sph_rt_rebuild_users():
#     pass
#
#
# @capp.task(base=BaseTask, name="vind.utils.async.functions.sph_rt_rebuild_address")
# def sph_rt_rebuild_address():
#     pass
#
#
# @capp.task(base=BaseTask, name="vind.utils.async.functions.sph_rt_rebuild_orders")
# def sph_rt_rebuild_orders():
#     pass


# @capp.task(base=BaseTask, name="vind.utils.async.functions.partner_remove_unaccepted")
# def partner_remove_unaccepted():
#     pass


@capp.task(base=BaseTask, name="vind.utils.async.functions.point_charge_process")
def point_charge_process():
    pass


# @capp.task(base=BaseTask, name="vind.utils.async.functions.point_charge_remove_outdated")
# def point_charge_remove_outdated():
#     pass

