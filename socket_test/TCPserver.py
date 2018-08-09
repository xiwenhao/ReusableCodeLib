#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: TCPserver.py
# @time: 2017/8/18 0018 下午 2:47
# @desc:
from time import sleep
import socket

ip_port = ('', 25555)
so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
so.bind(ip_port)
so.listen(3)

i = 50
conn, addr = so.accept()
while True:
    recv_data = conn.recv(1024)
    print str(recv_data).encode('utf-8')
    i -= 1
    sleep(1)
    if i == 0:
        conn.close()
        so.close()
        print 'server close...'
