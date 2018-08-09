#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: setTag.py
# @time: 2017/10/24 0024 上午 9:31
# @desc: {"port0": "port0", "tag1": "100", "port1": "port2", "tag2": "999"}

from subprocess import Popen, PIPE
from kafka import KafkaConsumer, KafkaProducer
import socket
import json

hostIP = socket.gethostbyname(socket.gethostname())
DEFAULT_BR = "br-int"
KAFKA = "192.168.100.15:9092"
CONFIG_TOPIC = hostIP + "_SET_TAG_CONFIG"
LOG_TOPIC = "SET_TAG_OPERATION"


def setTag(dict_):
    if not isinstance(dict_, dict):
        raise TypeError
    msg = ""
    handle = Popen("ovs-vsctl set port {port} tag={tag}".format(port=dict_["port0"], tag=dict_["tag0"]), stderr=PIPE)
    for i in handle.stderr.readlines():
        msg += i
    handle.kill()
    if "ovs-vsctl: no row" in msg:
        return "error", dict_["port0"]

    handle = Popen("ovs-vsctl set port {port} tag={tag}".format(port=dict_["port1"], tag=dict_["tag1"]), stderr=PIPE)
    for i in handle.stderr.readlines():
        msg += i
    handle.kill()
    if "ovs-vsctl: no row" in msg:
        return "error", dict_["port1"]


# 字典unicode转utf-8
def byteify(input_):
    if isinstance(input_, dict):
        return {byteify(key): byteify(value) for key, value in input_.iteritems()}
    elif isinstance(input_, list):
        return [byteify(element) for element in input_]
    elif isinstance(input_, unicode):
        return input_.encode('utf-8')
    else:
        return input_

def getConfigFromKafka():
    flag = True
    while flag:
        try:
            consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)
            while True:
                msg = next(consumer)
                cfg = byteify(json.loads(msg.value))
                if cfg["keys"] == "stop":
                    flag = False

                    break
                q.put(cfg)
                current_port = cfg["keys"]
        except Exception:
            continue
