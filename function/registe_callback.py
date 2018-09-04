#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/27 18:00
# @Author  : xwh
# @File    : registe_callback.py

import time
import functools


class Test(object):

    callback_list = []

    def feature(self):
        # feature将调用callback(), 但是在Test中并没有真正的定义callback
        for i in self.callback_list:
            if callable(i):
                i("event")

    def decorate(self, func):
        self.callback = func
        return func

    def decarate_list(self, func):
        self.callback_list.append(func)
        return func

test = Test()


# 将foo注册为回调函数
@test.decarate_list
def foo1(*w):
    print "foo1"

@test.decarate_list
def foo2(*w):
    print "foo2"+w[0]

@test.decarate_list
def foo3(s):
    print "foo3"+s


# 调用feature将触发回调函数
test.feature()