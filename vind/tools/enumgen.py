# -*- coding:utf-8 -*-
__author__ = 'ery'


def enumgen(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums["reverse_mapping"] = reverse
    enums["__rm"] = reverse
    return type('Enum', (), enums)
