#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/9 11:40
# @Author  : xwh
# @File    : websocket_base.py


from flask import Flask, render_template, make_response
from flask import request
from flask_socketio import SocketIO
from flask_socketio import Namespace, send, emit, disconnect
import eventlet
from logging.handlers import TimedRotatingFileHandler
from flask_cors import *
import json
import logging
from memcache import Client
import shutil
import time
import re
import string
import random
import sys
import os
from urllib import urlopen
# from _para import Sftp, Timeout, HostRefuse, PasswordError


eventlet.monkey_patch()
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# @socketio.on('ssh_upload', namespace='/ssh')
# def upload(_dic):
#     global login_token
#         if _dic["current_part"] == total_part - 1:
#             log.warning("token %s --> upload data near complete" % token)
#             emit("ssh_upload_ack", {
#                 "cmd": "UploadToVM",
#                 "token": token,
#                 "status": "NearComplete",
#                 "errmsg": ""
#             })
#             sftp.current_part = -1
#             emit("ssh_upload_ack", {
#                 "cmd": "UploadToVM",
#                 "token": token,
#                 "status": "Complete",
#                 "errmsg": ""
#             })


