#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: off_veth1.py
# @time: 2017/10/31 0031 上午 9:16
# @desc:
import os
import time

time.sleep(10)

os.system("ifconfig v-eth1 down")