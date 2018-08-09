#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: my_flask_site.py
# @time: 2017/12/20 0020 下午 4:45
# @author: xwh
# @desc:

from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from gevent import monkey
from flask import Flask, request, make_response
from Zabbix import Zab
import json
import time
from geventwebsocket import WebSocketError
monkey.patch_all()



class WSmanager(object):
    class Host(object):
        def __init__(self, host_name, item_list):
            self.host_name = host_name
            self.item_list = item_list

        def addInfo(self, item_list):
            self.item_list.extend(item_list)

    def __init__(self):
        self.host_list = []
        self.ws_list = []

    def addHost(self, host, item_list):
        host = self.Host(host, item_list)
        self.host_list.append(host)

    def sendMSG(self):
        for ws in self.ws_list:
            try:
                for host in self.host_list:
                    for item in host.item_list:
                        msg = zab.getInfoByItem(item)
                        ws.send(msg)
            except WebSocketError:
                self.ws_list.pop(ws)
                print "%s quit!" % ws
                continue


app = Flask(__name__)
zab = Zab(login="Admin", password="zabbix", base_url="http://192.168.100.101")
ws_manager = WSmanager()


@app.route("/")
def hello():

    return "connect OK\n"


@app.route('/capConfList', methods=['POST'])
def capConfList():
    postDataStr = request.get_data()
    postDataDict = json.loads(postDataStr)
    print postDataStr
    print type(postDataDict)
    host = postDataDict["host"].split()
    ws_manager.addHost()

    # hostip = postDataDict["hostip"]


    # retDict = { 'hostip': hostip,
    #             'confSer' : ('STATUS_KVM', 'STATUS_MIRROR', 'STATUS_KVMOB_F', 'STATUS_KVMOB_S', 'STATUS_KVMOB_U', 'STATUS_OVS',),
    #             'unconfSer': ('STATUS_DOCKER','STATUS_DOCKEROB',),
    #             }

    # response = make_response(json.dumps(retDict))
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Methods'] = 'PUT'
    # return response
    return "OK"

@app.route("/echo", methods=["POST", "GET"])
def addLiveUpdateObj():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        data = request.get_data()
        while True:
            # print ws.receive() 阻塞
            ws.send(str(ws)+ str(time.time()))
            time.sleep(0.2)

        return "OK\n"
        #host_list = []
        #ws_manager.addWS2Host(ws_fd=ws, host_list=host_list)


if __name__ == '__main__':
    ssl = {
        "certfile": "E:\\Share\\xwh_zabbix_py\\server.crt",
        "keyfile": "E:\\Share\\xwh_zabbix_py\\server.key",
        "ciphers": "RC4"
    }
    http_server = WSGIServer(('0.0.0.0', 9000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
