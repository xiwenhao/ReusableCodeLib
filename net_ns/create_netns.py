#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: create_netns.py
# @time: 2017/12/8 0008 下午 1:27
# @author: xwh
# @desc:
import os
from subprocess import Popen, PIPE


def createNetns(ns_name):
    os.system("ip netns del {ns_name} &> /dev/null")
    handler = Popen("ip netns add {ns_name}".format(ns_name=ns_name), shell=True, stdout=PIPE, stderr=PIPE)
    if handler.stderr.readline().__len__() != 0:
        handler.kill()
        return False
    else:
        handler.kill()
        return True
