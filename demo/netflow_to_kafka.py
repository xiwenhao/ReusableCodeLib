#!/usr/bin/env python
# -*- coding:utf-8 -*-

# @company: heetian
# @file: netflow_to_kafka.py
# des: 监听netflow报文发送到kafka
# https://wenku.baidu.com/view/8806d77c02768e9951e7381f.html?qq-pf-to=pcqq.c2c

import socket
import binascii
import json
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from kafka import KafkaProducer


KAFKA = "192.168.100.15:9092"
PRODUCER_TOPIC = "STATUS_OVS"
LOG_TOPIC = "OPERATION"
UDP_IP = "0.0.0.0"
UDP_PORT = 2055

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
producer = KafkaProducer(bootstrap_servers=KAFKA)


# 配置logging
class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)

    def flush(self):
        pass

log = logging.getLogger()
file_name = "./NetFlowAnalysis.log"
logformatter = logging.Formatter('%(asctime)s %(lineno)d [%(levelname)s] | %(message)s')
loghandler = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
loghandler.setFormatter(logformatter)
loghandler.suffix = "%Y-%m-%d"
log.addHandler(loghandler)
log.setLevel(logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logformatter)
logging.getLogger('').addHandler(console)
redirectStd = LoggerWriter(log, logging.INFO)
sys.stderror = redirectStd
sys.stdout = redirectStd
log_producer = KafkaProducer(bootstrap_servers=KAFKA)


# hex2dec function
def h2d(string_num):
    return str(int(string_num.upper(), 16))

while True:
    result = {}
    result.clear()
    logging.info("waiting gram...")
    log_producer.send(LOG_TOPIC, "waiting gram")
    logging.info("recv gram")
    data, addr = sock.recvfrom(1500)
    logging.info("recv gram ok")
    log_producer.send(LOG_TOPIC, "recv gram")
    # print binascii.hexlify(data)
    # 报文被转换成了16进制 长度增加了一倍

    nfGram = binascii.hexlify(data[24:-1])
    nfGramHeader = binascii.hexlify(data[0:24])

    version = h2d(nfGramHeader[0:4])
    count = h2d(nfGramHeader[4:8])
    sys_uptime = h2d(nfGramHeader[8:16])
    unix_secs = h2d(nfGramHeader[16:24])
    unix_nsecs = h2d(nfGramHeader[24:32])
    flow_seq = h2d(nfGramHeader[32:40])
    engine_type = h2d(nfGramHeader[40:42])
    engine_id = h2d(nfGramHeader[42:44])

    # ip_addr
    src_ip = h2d(nfGram[0:2]) + "." + h2d(nfGram[2:4]) + "." + h2d(nfGram[4:6]) + "." + h2d(nfGram[6:8])
    dst_ip = h2d(nfGram[8:10]) + "." + h2d(nfGram[10:12]) + "." + h2d(nfGram[12:14]) + "." + h2d(nfGram[14:16])
    next_hop = h2d(nfGram[16:24])
    snmp_input = h2d(nfGram[24:28])
    snmp_output = h2d(nfGram[28:32])
    dpkts = h2d(nfGram[32:40])
    doctets = h2d(nfGram[40:48])
    first = h2d(nfGram[48:56])
    last = h2d(nfGram[56:64])
    src_port = h2d(nfGram[64:68])
    dst_port = h2d(nfGram[68:72])
    tcp_flags = h2d(nfGram[74:76])
    proto = h2d(nfGram[76:78])
    tos = h2d(nfGram[78:80])
    src_as = h2d(nfGram[80:84])
    dst_as = h2d(nfGram[84:88])
    src_mask = h2d(nfGram[88:90])
    dst_mask = h2d(nfGram[90:92])

    result["src_ip"] = src_ip
    result["dst_ip"] = dst_ip
    result["next_hop"] = next_hop
    result["snmp_input"] = snmp_input
    result["snmp_output"] = snmp_output
    result["dpkts"] = dpkts
    result["doctets"] = doctets
    result["first"] = first
    result["last"] = last
    result["src_port"] = src_port
    result["dst_port"] = dst_port
    result["tcp_flags"] = tcp_flags
    result["proto"] = proto
    result["tos"] = tos
    result["src_as"] = src_as
    result["dst_as"] = dst_as

    result["version"] = version
    result["count"] = count
    result["sys_uptime"] = sys_uptime
    result["unix_secs"] = unix_secs
    result["unix_nsecs"] = unix_nsecs
    result["flow_seq"] = flow_seq
    result["engine_type"] = engine_type
    result["engine_id"] = engine_id
    result["src_mask"] = src_mask
    result["dst_mask"] = dst_mask
    s = json.dumps(result)
    producer.send(PRODUCER_TOPIC, s)
    logging.info("producer result to kafka")
    log_producer.send(LOG_TOPIC, "prodecer result to kafka")
