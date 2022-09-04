# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 14:01:31 2022

@author: ScottStation
"""

from functools import wraps


def get_mac_address():
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8],mac[8:10], mac[10:])


def assert_auth(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        from .client import qedataClient
        if not qedataClient.check_auth():
            print("您还没有获得授权，请先在quantease官网获取授权码，详见https://quantease.cn/newdoc/auth.html")
        else:
            return func(*args, **kwargs)
    return _wrapper
