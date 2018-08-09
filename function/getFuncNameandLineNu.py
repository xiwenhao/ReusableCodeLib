#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/26 11:50
# @Author  : xwh
# @File    : getFuncNameandLineNu.py
# import sys
#
# func_name = sys._getframe().f_back.f_code.co_name
# lineNumber = sys._getframe().f_back.f_lineno



import inspect, json
def get_current_function_name():
    return inspect.stack()[1][3]

def foo():
    print get_current_function_name()
    return 1

print foo()