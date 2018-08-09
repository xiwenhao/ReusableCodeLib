#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: server.py
# @time: 2017/8/30 0030 下午 4:56
# @desc:
import socket
import pickle

HOST='localhost'
PORT=50007
s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1)
while 1:
       conn,addr=s.accept()
       while 1:
        data=conn.recv(128)
        print type(pickle.loads(data))
        print data
