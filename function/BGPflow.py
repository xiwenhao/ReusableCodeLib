#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: BGPflow.py
# @time: 2017/10/9 0009 上午 10:22
# @desc:{"operation":"add_flow", "src_port":"", "dst_port":""}

from subprocess import PIPE, Popen
from kafka import KafkaConsumer, KafkaProducer
import os
import multiprocessing as mp
import socket
import json
import time


DEFAULT_NIC = "br-int"
KAFKA = "192.168.100.15:9092"
CONFIG_TOPIC = "FLOW_TABLE_CONFIG"
LOG_TOPIC = "BGPflow"
hostIP = socket.gethostbyname(socket.gethostname())


def getPortInformation():
    port_dict = dict()
    handle = Popen("ovs-ofctl show %s" % DEFAULT_NIC, stdout=PIPE, shell=True, stderr=PIPE)
    all_info = handle.stdout.readlines()
    handle.kill()
    for each in all_info:
        if "addr" in each:
            temp = each.split('(')
            num = temp[0].strip()
            port = temp[1].split(')')[0]
            port_dict[port] = num
    return port_dict


def matchPort(*name):
    port_dict = getPortInformation()
    for each in name:
        try:
            port_dict[each]
        except KeyError:
            return False
    return True


def addFlowTable(src_port, dst_port):
    port_dict = getPortInformation()
    # 86(qvo4e119bc5-ca): addr:92:33:61:66:bf:0f
    try:
        os.popen('ovs-ofctl add-flow %s "in_port=%s,actions=output:%s"' % (
            DEFAULT_NIC, port_dict[src_port], port_dict[dst_port]))
        return True
    except KeyError:
        return False


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


def msgGeneration(cmd, **kwargs):
    if cmd == "heartbeat":
        return {
             "cmd": "heartbeat",
             "type": "BGPflow",
             "message": {
                 "ip": hostIP,
                 "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
             }
        }
    if cmd == "echo":
        return {
            "cmd": "echo",
            "type": "BGPflow",
            "message": {
                "ip": hostIP,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "cfg": kwargs["echo_info"]
            }
        }
    if cmd == "error":
        return {
            "cmd": "error",
            "type": "BGPflow",
            "message": {
                "ip": hostIP,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "error_cfg": kwargs["error_info"]
            }
        }
    if cmd == "stop":
        return {
            "cmd": "stop",
            "type": "BGPflow",
            "message": {
                "ip": hostIP,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            }
        }
    if cmd == "start":
        return {
            "cmd": "start",
            "type": "BGPflow",
            "message": {
                "ip": hostIP,
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            }
        }


def sendLog(msg):
    log_producer = KafkaProducer(bootstrap_servers=KAFKA)
    log_producer.send(LOG_TOPIC, json.dumps(msg))
    log_producer.flush()
    log_producer.close()


def heartBeat(que):
    time.sleep(1)
    while True:
        if que.empty() is False:
            break
        sendLog(msgGeneration("heartbeat"))
        time.sleep(10)
# def dpMirror(src_port, dst_port):
#     # 此处的port全是网络接口, 并非五元组中的端口
#     handle = Popen('ovs-vsctl -- set bridge {br} mirrors=@m \
#         -- --id=@{src_NETport} get port {src_NETport} \
#         -- --id=@{dst_NETport} get port {dst_NETport} \
#         -- --id=@m create mirror name=mymirror select-dst-port=@{src_NETport} \
#         select-src-port=@{dst_NETport} output-port=@{dst_NETport}'.format(
#         br = DEFAULT_NIC, src_NETport=src_port, dst_NETport=dst_port))

if __name__ == '__main__':
    q = mp.Queue(1)
    consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)
    p1 = mp.Process(target=heartBeat, args=(q,))
    p1.start()
    start_msg = msgGeneration("start")
    sendLog(start_msg)
    while True:
        msg = next(consumer)
        # {"operation":"add_flow", "src_port":"", "dst_port":""}
        # {"operation":"stop", "src_port":"", "dst_port":""}
        cfg = byteify(json.loads(msg.value))

        if matchPort(cfg["src_port"], cfg["dst_port"]) is False:
            error_msg = msgGeneration("error", error_info=cfg)
            sendLog(error_msg)
            continue
        if cfg["operation"] == "stop":
            q.put("stop")
            sendLog(msgGeneration("stop"))
            break
        if cfg["operation"] == "clear":
            pass
        if cfg["operation"] == "clear_all":
            pass
        if cfg["operation"] == "add_flow":
            addFlowTable(cfg["src_port"], cfg["dst_port"])
            sendLog(msgGeneration("echo", echo_info=cfg))

    p1.join()
