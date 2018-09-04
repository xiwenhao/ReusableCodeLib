#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/25 17:24
# @Author  : xwh
# @File    : reboot_self_subprocess.py

from multiprocessing import Process

class RebootSelf():

    def __init__(self):
        _global = globals()
        if "multiprocessing" not in _global:
            import multiprocessing
        pass