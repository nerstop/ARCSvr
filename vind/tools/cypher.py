# -*- coding:utf-8 -*-
__author__ = 'ery'

from Crypto.Cipher import AES

__PASSCODE__ = "3af8786594799b61b7511674fa30d65b"


def _padding(msg):
    r = msg.__len__() % 16
    if r == 0:
        return msg
    else:
        for i in range(16 - r):
            msg += " "
        return msg


def aes256_encode(msg, passcode=__PASSCODE__):
    return AES.new(passcode).encrypt(msg)


def aes256_decode(cypered, passcode=__PASSCODE__):
    return AES.new(passcode).decrypt(cypered)
