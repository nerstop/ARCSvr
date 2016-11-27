# -*- coding:utf-8 -*-
__author__ = 'ery'


class StrCat(object):
    def __init__(self, seed = None):
        from cStringIO import StringIO
        self._str = StringIO()
        if seed:
            assert isinstance(seed, str)
            self._str.write(seed)

    def __enter__(self):
        return self

    def __exit__(self):
        self._str.close()

    def __str__(self):
        return self._str.getvalue()

    def __unicode__(self):
        return unicode(self._str.getvalue(), "utf8")

    def append(self, token):
        assert isinstance(token, str)
        self._str.write(token)

