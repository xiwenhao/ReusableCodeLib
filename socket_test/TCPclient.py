#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: TCPclient.py
# @time: 2017/8/18 0018 下午 2:55
# @desc:

from time import sleep
import socket

addr = ('192.168.100.16', 25555)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.connect(addr)
i = 0
while True:
    i += 1
    sk.send(('hello %s' %i).decode('utf-8'))
    sleep(1)
