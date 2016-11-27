# -*- coding:utf-8 -*-

import zlib
import cPickle as pickle
import datetime
import time


class SerializerMixin(object):
    def serialize(self, fields=[], exclude=[], origin_class=None):
        result = dict()
        exclude_fields = exclude or []
        if not exclude_fields:
            exclude_fields.append("passwd")
        if hasattr(self, "exclude_fields"):
            exclude_fields = getattr(self, "exclude_fields")
        if not fields:
            if hasattr(self, "_sa_class_manager"):
                fields = getattr(self, "_sa_class_manager").keys()
            elif hasattr(self, "fields"):
                fields = getattr(self, "fields")
            else:
                return result
        for field in fields:
            if field in exclude_fields:
                continue
            if hasattr(self, field):
                value = getattr(self, field)
            else:
                continue
            value = self._get_cleaned_value(value, origin_class)
            if value is not None:
                result[field] = value

        if hasattr(self, "get_external_data"):
            f = getattr(self, "get_external_data")
            result.update(f())
        return result

    def _get_cleaned_value(self, value, origin_class=None):
        if origin_class is not None and isinstance(value, origin_class):
            return None
        if isinstance(value, self.__class__):
            if hasattr(self, "self_fields"):
                fields = getattr(self, "self_fields")
                return value.serialize(fields)
            else:
                return value.serialize()
        elif isinstance(value, list):
            return [v.serialize(origin_class=self.__class__) for v in value]
        elif isinstance(value, datetime.date):
            return time.mktime(value.timetuple())
        elif SerializerMixin in value.__class__.__bases__:
            return value.serialize()
        else:
            return value


def zp(_obj):
    return zlib.compress(pickle.dumps(_obj, pickle.HIGHEST_PROTOCOL), 1)


def pz(_str):
    return pickle.loads(zlib.decompress(_str))
