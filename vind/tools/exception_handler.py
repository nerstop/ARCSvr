# -*- coding:utf-8 -*-
__author__ = 'ery'

# print "[<-] %s" % (__name__,)

import linecache, traceback
import sys, os


# def format_exception():
#     exc_type, exc_obj, tb = sys.exc_info()
#     f = tb.tb_frame
#     lineno = tb.tb_lineno
#     filename = f.f_code.co_filename
#     linecache.checkcache(filename)
#     line = linecache.getline(filename, lineno, f.f_globals)
#     return """EXCEPTION IN ({}, LINE {} "{}"): {}""".format(filename, lineno, line.strip(), exc_obj)

# _virtualenv_paths = None


# def get_virtualenv_paths():
#     global _virtualenv_paths
#     if _virtualenv_paths:
#         return _virtualenv_paths
#     import os, sys, virtualenv
#     _excutable_path = os.path.split(sys.executable)[0]
#     if "/bin" in _excutable_path.lower():
#         virtualenv_path = os.path.split(_excutable_path)[0]
#     else:
#         virtualenv_path = _excutable_path
#     _virtualenv_paths = virtualenv.path_locations(virtualenv_path)
#     return _virtualenv_paths


def format_exception():
    _, exc_obj, tb = sys.exc_info()

    if tb is not None:
        # venv_lib_path = get_virtualenv_paths()[1].lower()
        hint = "lib/python2.7"
        tb_found = False
        for file_path, lineno, func_name, _ in reversed(traceback.extract_tb(tb)):
            # 아래에서 위로
            # if file_path.lower().startswith(venv_lib_path):
            if hint in file_path.lower():
                if tb_found:
                    break
            else:
                file_path = file_path
                file_name = os.path.split(file_path)[1]
                lineno = lineno
                func_name = func_name
                tb_found = True
            # if not file_path.lower().startswith(venv_lib_path):
            #     file_name = os.path.split(file_path)[1]
            #     lineno = lineno
            #     func_name = func_name
            #     tb_found = True
            #     break

            # if file_path.lower().startswith("/vind/vind/"):
            #     file_name = os.path.split(file_path)[1]
            #     lineno = lineno
            #     func_name = func_name
            #     tb_found = True

        if not tb_found:
            file_path, lineno, func_name, _ = traceback.extract_tb(tb)[-1]
            file_name = os.path.split(file_path)[1]
            lineno = lineno
            func_name = func_name

        f = tb.tb_frame
        linecache.checkcache(file_path)
        line = linecache.getline(file_path, lineno, f.f_globals)
        return """ @#! EXCEPTION IN (`{}` OF {}, LINE {} "{}"): {}""".\
            format(func_name, file_name, lineno, line.strip(), exc_obj)
    else:
        return None


def dict_exception(codelines=5):
    def extract(file_path, lineno, func_name, _globals):
        file_name = os.path.split(file_path)[1]
        linecache.checkcache(file_path)
        phrase = linecache.getline(file_path, lineno, _globals)
        lines = []
        line_min = lineno - codelines if lineno - codelines >= 0 else 0
        for ln in range(line_min, lineno + 2):
            try:
                l = linecache.getline(file_path, ln, _globals)
                if len(l) > 0:
                    lines.append(l)
            except Exception:
                continue
        if len(lines) > 0:
            lines = "".join(lines)
        if len(lines) == 0:
            lines = None

        # print file_name, file_path, lines, func_name, phrase

        return {"filename": file_name.strip(), "filepath": file_path.strip(), "lineno": lineno, "lines": lines,
                "funcname": func_name.strip(), "phrase": phrase.strip(), "description": exc_obj}

    _, exc_obj, tb = sys.exc_info()
    if tb:
        # venv_lib_path = get_virtualenv_paths()[1].lower()
        # print(venv_lib_path)
        hint = "lib/python2.7"
        origin_file_path = ""
        origin_lineno = 0
        origin_func_name = ""
        tb_found = False
        full_tb = []
        for file_path, lineno, func_name, _ in reversed(traceback.extract_tb(tb)):
            # 아래서부터 위로
            # if file_path.lower().startswith(venv_lib_path):
            if hint in file_path.lower():
                if tb_found:
                    break
            else:
                origin_file_path = file_path
                origin_lineno = lineno
                origin_func_name = func_name
                tb_found = True
            full_tb.append((file_path, lineno, func_name, tb.tb_frame.f_globals))

        file_path, lineno, func_name, _ = traceback.extract_tb(tb)[-1]
        term_file_path = file_path
        # term_file_path = os.path.split(file_path)[1]
        term_lineno = lineno
        term_func_name = func_name

        rt = {}

        if tb_found:
            if origin_file_path != term_file_path or origin_lineno != term_lineno:
                rt["original"] = extract(origin_file_path, origin_lineno, origin_func_name, tb.tb_frame.f_globals)

            if origin_file_path == term_file_path and origin_lineno == term_lineno:
                # 맨 마지막줄과, 찾은 첫 근원줄이 동일하다.
                # 동일하다면 맨 마지막줄만 처리한다.
                rt["traceback"] = [extract(term_file_path, term_lineno, term_func_name, tb.tb_frame.f_globals)]
            else:
                # 동일하지 않다.
                # rt["original"] = extract(origin_file_path, origin_lineno, origin_func_name, tb.tb_frame.f_globals)
                # rt["terminal"] = extract(term_file_path, term_lineno, term_func_name, tb.tb_frame.f_globals)
                rt["traceback"] = [extract(*tb) for tb in reversed(full_tb)]
        else:
            # 근원이 되는 stack 을 못 찾았다.
            # rt["terminal"] = extract(term_file_path, term_lineno, term_func_name, tb.tb_frame.f_globals)
            rt["traceback"] = [extract(*tb) for tb in reversed(full_tb)]

        return rt
    else:
        return None


def print_exception():
    # exc_type, exc_obj, tb = sys.exc_info()
    # f = tb.tb_frame
    # lineno = tb.tb_lineno
    # filename = f.f_code.co_filename
    # linecache.checkcache(filename)
    # line = linecache.getline(filename, lineno, f.f_globals)
    # print("""EXCEPTION IN ({}, LINE {} "{}"): {}""".format(filename, lineno, line.strip(), exc_obj))
    print(format_exception())


def send_exception_to_slack():
    # 구현요망
    pass

# print "[->] %s" % (__name__,)
