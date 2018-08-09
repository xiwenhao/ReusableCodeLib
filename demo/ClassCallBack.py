#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/11 14:38
# @Author  : xwh
# @File    : ClassCallBack.py
import weakref

class callback_base(object):
    subclass = []
    def __init__(self, name):
        self.__class__.subclass.append(weakref.proxy(self, self.delTrigger))
        self.name = name
    @staticmethod
    def delTrigger(*args):
        print "del",args

class foo(callback_base):
    pass

if __name__ == '__main__':
    mycallback = foo("bar")
    for instance in callback_base.subclass:
        print instance


