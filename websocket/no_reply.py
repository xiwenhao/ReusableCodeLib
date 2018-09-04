#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: no_reply.py
# @time: 2018/1/25 0025 下午 3:53
# @author: xwh
# @desc:

from flask import Flask, render_template, make_response
from flask import request
from flask_socketio import SocketIO
from flask_socketio import Namespace, send, emit, disconnect
import eventlet
import threading
from logging.handlers import TimedRotatingFileHandler
from flask_cors import *
import json, sys
import logging


eventlet.monkey_patch()
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')


def thtask(dir, filename, data):
    with open(dir+filename, "w") as f:
        f.write(data)
    print "write %s done" % dir+filename


@socketio.on('upload', namespace='/upload')
def msg_handle(_dic):
    _dir = "/home/xwh/zabbix_py/web/test/"
    filename = _dic["index"]
    data = _dic["data"]
    # print filename
    emit("upload_ack", {
        "index": _dic["index"]
    })


if __name__ == '__main__':
    port = sys.argv[1]
    print "listen port %s, start listen " % sys.argv[1]
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
