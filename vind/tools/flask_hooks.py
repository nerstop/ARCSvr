# -*- coding:utf-8 -*-
__author__ = 'ery'

import logging
# import datetime
try:
    import ujson as json
except ImportError:
    import json

from time import time as stime
from flask import current_app, request, session

# from vind import sentry
# from vind.tools import GS
from vind.tools import parse_session
from vind.tools import dict_exception

cl = logging.getLogger(__name__)


def pre_request_logging():
    __enter_timestamp = stime()
    # if not GS.is_production():
    session["__enter_timestamp"] = __enter_timestamp
    s = ""
    if request.data.__len__() > 0:
        try:
            d = json.loads(unicode(request.data, "utf8"))
            s = json.dumps(d, indent=4, sort_keys=True)
        except Exception:
            # sentry.captureException()
            pass

    if len(s) == 0:
        s = "(Empty request data)"

    cl.debug("\n".join(["\n" + "<" + "-" * 79,
        request.remote_addr + " -> " + request.method + " " + request.url,
        s,
        ", ".join([": ".join(x) for x in request.headers])])
    )


def after_request_logging(response):
    __exit_timestamp = stime()

    def generate_slack_log_args(__exit_timestamp, have_exception=False):
        resd = {"status_code": response.status_code,
                "data": unicode(response.get_data(), "utf8") if not have_exception else None,
                "__exit_timestamp": __exit_timestamp}
        _, _, users_id = parse_session()
        if users_id is None:
            users_id = "ANONYMOUS"

        reqd = {"remote_addr": request.remote_addr,
                "method": request.method,
                "url": request.url,
                "__enter_timestamp": session.get("__enter_timestamp", 0)}
        if request.data and len(request.data) > 0:
            reqd["data"] = unicode(request.data, "utf8")
        else:
            reqd["data"] = None
        # 일단은 쓰지 않으니 임시적으로 None 을 먹인다.
        reqd["headers"] = None
        if have_exception:
            de = dict_exception()
        else:
            de = None
        return reqd, resd, users_id, de

    # is_production = GS.is_production()
    is_production = False
    if is_production:
        # (400, 500) 에러가 있는게 아니면 무시한다.
        # if response and response.status_code in (400, 500):
        #     slack_post_report_request.apply_async(args=generate_slack_log_args(__exit_timestamp, True))
        pass
    else:
        # 구구절절 다 적어준다.
        if response and hasattr(response, "status_code"):
            # if response.status_code in (400, 404, 500):
            #     slack_post_report_request.apply_async(args=generate_slack_log_args(__exit_timestamp, True))
            # elif response.status_code in (200, 401):
            #     slack_post_report_request.apply_async(args=generate_slack_log_args(__exit_timestamp, False))

            try:
                raw = response.get_data()
                if raw and len(raw) > 0:
                    d = json.loads(unicode(response.get_data(), "utf8"))
                    # cl.debug("\n" + "\n".join([json.dumps(d, indent=4, sort_keys=True), "-" * 79 + ">"]))
                    cl.debug("\n" + json.dumps(d, indent=4, sort_keys=True))
            except Exception as err:
                # sentry.captureException()
                print(str(err))

    return response

    # resd = {"status_code": 502, "data": None, "__exit_timestamp": stime()}
    # _, _, users_id = parse_session()
    # if users_id is None:
    #     users_id = "ANONYMOUS"
    #
    # reqd = {"remote_addr": request.remote_addr, "method": request.method, "url": request.url, \
    #         "__enter_timestamp": session.get("__enter_timestamp", 0)}
    # if request.data and len(request.data) > 0:
    #     reqd["data"] = unicode(request.data, "utf8")
    # else:
    #     reqd["data"] = None
    # # 일단은 쓰지 않으니 임시적으로 None 을 먹인다.
    # reqd["headers"] = None
    # de = None
    #
    # is_production = GS.is_production()
    # if response:
    #     resd["status_code"] = response.status_code
    #     if is_production:
    #         # 400, 500 에러만 잡는다.
    #         if hasattr(response, "status_code") and response.status_code in (400, 500):
    #             de = dict_exception()
    #             slack_post_report_request.apply_async(args=(reqd, resd, users_id, de))
    #     else:
    #         # 200, 400, 401, 404, 500 을 잡는다.
    #         if hasattr(response, "status_code"):
    #             if response.status_code in (400, 404, 500):
    #                 de = dict_exception()
    #                 slack_post_report_request.apply_async(args=(reqd, resd, users_id, de))
    #             elif response.status_code in (200, 401):
    #                 resd["data"] = unicode(response.get_data(), "utf8")
    #                 de = ""
    #                 slack_post_report_request.apply_async(args=(reqd, resd, users_id, de))

    # if (not is_production) and response:
    #     try:
    #         raw = response.get_data()
    #         if raw and len(raw) > 0:
    #             d = json.loads(unicode(response.get_data(), "utf8"))
    #             # cl.debug("\n" + "\n".join([json.dumps(d, indent=4, sort_keys=True), "-" * 79 + ">"]))
    #             cl.debug("\n" + json.dumps(d, indent=4, sort_keys=True))
    #     except Exception:
    #         sentry.captureException()
    #
    # return response

exec_teardown_request_handler = """
def teardown_request_handler(exception):
    if exception:
        sentry.captureException()

    try:
        db.remove()
    except Exception as e:
        print(e)

    cl.debug("\\n%s>" % ("-" * 79,))
"""

# eval_teardown_request_handler = """
# def teardown_request_handler(exception):
#     if exception:
#         sentry.captureException()
#
#     # import sys
#     # caller_globals = sys._getframe(1).f_globals
#     # ks =  caller_globals.keys()
#     # ks.sort()
#     # for k in ks:
#     #     print k
#     # for d in range(10):
#     #     try:
#     #         print "----- depth=%d" % (d,)
#     #         print "--- local"
#     #         _locals = sys._getframe(d).f_locals
#     #         ks = _locals.keys()
#     #         ks.sort()
#     #         for k in ks:
#     #             print "\t" + k
#     #         print "--- global"
#     #         _globals = sys._getframe(d).f_globals
#     #         ks = _globals.keys()
#     #         ks.sort()
#     #         for k in ks:
#     #             print "\t" + k
#     #         # print "--- builtins"
#     #         # _builtins = sys._getframe(d).f_builtins
#     #         # ks = _builtins.keys()
#     #         # ks.sort()
#     #         # for k in ks:
#     #         #     print "\t" + k
#     #     except Exception as e:
#     #         print e
#     #         break
#
#
#     # caller_locals = sys._getframe(2).f_locals
#     # ks = caller_locals.keys()
#     # ks.sort()
#     # for k in ks:
#     #     print k
#     # for k in dir(sys.modules[__name__]):
#     #     print k
#     # for k in locals().keys():
#     #     print k
#
#     # if "db" in caller_locals:
#     try:
#         # db = caller_locals["db"]
#         db.remove()
#     except Exception as e:
#         print e
#         pass
#         # sentry.captureException()
#     cl.debug("\n" + "-" * 79 + ">")
# """
