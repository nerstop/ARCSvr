# -*- coding:utf-8 -*-
__author__ = 'ery'

import ujson as json

from celery import Task, signals

from sqlalchemy import func, or_, and_, text
from vind.tools import DB, RLock
from vind.models import *
from vind.utils.async import capp, logger, BaseTask, NoResultTask
from vind.config import push_message_codes


@capp.task(base=NoResultTask, name="vind.message.sned_regen_password_email")
def sned_regen_password_email(from_address, to_address, new_password):
    # print "vind.message.regen_password"
    import re
    email_regex = re.compile(r"([\d\w\_\-\.]+@[\d\w\_\-\.]+)")
    if (email_regex.findall(from_address)[0] == from_address) and (email_regex.findall(to_address)[0] == to_address):
        # 여기서 메일을 좀 보내줘야지
        return True
    else:
        logger.error("#1 Invalid email address, %s, %s" % (from_address, to_address))
        return False


@capp.task(base=NoResultTask, name="vind.message.android_push")
def android_push(uuids, message):
    # print "vind.message.android_push"

    if not uuids:
        return False

    from gcm import GCM

    g = GCM("AIzaSyAheYj04o3dgHhG8MrN5NGQKY4HT8NhzKc")

    try:
        if isinstance(uuids, (list, tuple, set)):
            g.json_request(registration_ids=uuids, data=message)
        elif isinstance(uuids, str):
            g.plaintext_request(registration_id=uuids, data=message)
    except Exception as e:
        logger.error("#1 %s" % (str(e),))
        return False
    return True


@capp.task(base=NoResultTask, name="vind.message.ios_push")
def ios_push(uuids, message):
    # print "vind.message.ios_push"

    if not uuids:
        return False

    from apns import APNs

    a = APNs(use_sandbox=False, cert_file="", key_file="")

    # https://github.com/djacobs/PyAPNs/blob/master/tests.py
    # http://pirtaja.tistory.com/entry/django%EB%A1%9C-ios-notification-server-%EB%A7%8C%EB%93%A4%EA%B8%B0

    return True


@capp.task(base=NoResultTask, name="vind.message.mpush")
def mpush(device_ids=None, users_idxs=None, pcode=None, message=None):
    # print "vind.message.mpush"

    if not pcode:
        logger.error("#1 pcode missing")
        return False

    if pcode not in push_message_codes:
        logger.error("#2 pcode not in push_message_codes, pcode : %d" % (pcode,))
        return False

    code = push_message_codes[pcode][0]

    if message:
        if isinstance(message, (str, unicode)):
            try:
                json.loads(message)
            except Exception:
                logger.error("#3 Invalid JSON : %s" % (message,))
                return False
            msg = {"code": code, "content": message}
        elif isinstance(message, (list, tuple, dict)):
            try:
                json_message = json.dumps(message)
            except Exception as e:
                logger.error("#4 Invalid data type, type : %s" % (str(type(message)),))
                # print "Invalid Data : %s" % (unicode(e),)
                return False
            msg = {"code": code, "content": json_message}
        else:
            logger.error("#5 message is exists, but i can't handle it, Type : %s" % (str(type(message)),))
            return False
    else:
        msg = {"code": code, "content": ""}

    # logger.error("mpush #1, msg(%s)" % (str(msg),))

    device_ids_set = set()
    if device_ids or users_idxs:
        if device_ids:
            if not isinstance(device_ids, (str, unicode, set, list, tuple)):
                # print type(device_ids)
                logger.error("#6")
                return False
            if isinstance(device_ids, (str, unicode)):
                device_ids_set.add(device_ids)
            elif isinstance(device_ids, (list, tuple)):
                device_ids_set = device_ids_set.union(device_ids)
            else:
                device_ids_set = device_ids_set.union(device_ids)
        if users_idxs:
            if not isinstance(users_idxs, (int, long, set, list, tuple)):
                # print type(users_idxs)
                logger.error("#7")
                return False
            if isinstance(users_idxs, (int, long)):
                try:
                    db = DB.get_session()
                    user = db.query(Users).filter_by(idx=users_idxs).first()
                    if user:
                        device_ids_set.add(user.device_id)
                except Exception as e:
                    logger.error("#8 %s" % (str(e),))
                finally:
                    if "db" in locals() and hasattr(db, "remove"):
                        db.remove()
            else:
                try:
                    db = DB.get_session()
                    users = db.query(Users.device_id).filter(Users.idx.in_(users_idxs)).all()
                    if users and (users.__len__() > 0):
                        device_ids_set = device_ids_set.union(map(lambda u: u[0], users))
                except Exception as e:
                    logger.error("#9 %s" % (str(e),))
                finally:
                    if "db" in locals() and hasattr(db, "remove"):
                        db.remove()

    # logger.error("mpush #2, device_ids_set(%s)" % (str(device_ids_set),))
    if device_ids_set.__len__() > 0:
        # 없거나 비어있는 것들을 제거한다.
        device_ids_set.difference_update((None, ""))

        device_ids = tuple(device_ids_set)

        # logger.error("mpush #3, device_ids(%s)" % (str(device_ids),))

        uuid_android = []
        uuid_ios = []

        for uuid in device_ids:
            if int(uuid[:2]) == 0:
                uuid_android.append(uuid[3:])
            elif int(uuid[:2]) == 1:
                uuid_ios.append(uuid[3:])
            else:
                logger.error("#10 Invalid uuid form : %s" % (uuid,))

        chunk_size = GS.getd("VAR_CELERY_PUSH_CHUNK_SIZE")
        if uuid_android.__len__() > 0:
            # logger.error("mpush #4-1, uuid_android(%s)" % (str(uuid_android),))

            for i in xrange((uuid_android.__len__() / chunk_size) + 1):
                android_push.apply_async(args=(uuid_android[i * chunk_size: (i + 1) * chunk_size], msg))
        if uuid_ios.__len__() > 0:
            # logger.error("mpush #4-2, uuid_ios(%s)" % (str(uuid_ios),))

            for i in xrange((uuid_ios.__len__() / chunk_size) + 1):
                ios_push.apply_async(args=(uuid_ios[i * chunk_size: (i + 1) * chunk_size], msg))

    return True
