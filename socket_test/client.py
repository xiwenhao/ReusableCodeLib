#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: client.py
# @time: 2017/8/30 0030 下午 4:57
# @desc:
#!/usr/bin/python
import socket
import pickle

HOST='localhost'
PORT=50007
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))
i = 1
data = ['q','w','e']
while 1:
    s.sendall(pickle.dumps(data))
    print 'send',i
    i += 1
