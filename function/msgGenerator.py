#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: msgGenerator.py
# @time: 2017/10/24 0024 下午 2:34
# @desc:

import time
import socket


hostIP = socket.gethostbyaddr(socket.gethostname())


def msgGenerator(msg_type, **kwargs):
    if msg_type == "heartbeat":
        return {
             "cmd": "detele",
             "type": "BGPmirror",
             "message": {
                 "ip": hostIP,
                 "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                 "heartbeat_info": kwargs["heartbeat_info"]
             }
        }