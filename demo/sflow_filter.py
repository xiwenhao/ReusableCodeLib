#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: sflow_filter.py
# @time: 2017/9/14 0014 下午 3:27
# @desc:
# filter msg {"evidence":"src_ip","agent":"192.168.100.13","filter":"192.168.1.82", "mode":"filter"}
# evidence: src_ip; dst_ip; src_mac; dst_mac 过滤的依据
# agent_ip: 需要过滤的agent
# filter: 过滤
# mode: filter or none

from subprocess import Popen, PIPE
from kafka import KafkaProducer
import multiprocessing as mp
import socket
import json
import time
import sys


KAFKA = "192.168.100.15:9092"
PRODUCER_TOPIC = "STATUS_OVS"
CONFIG_TOPIC = "SFLOW_FILTER_CONFIG"
LOG_TOPIC = "OPERATION"
SFLOW_PORT = 6343

# 宿主机ip
hostIP = socket.gethostbyname(socket.gethostname())

# # 配置logging
# class LoggerWriter:
#     def __init__(self, logger, level):
#         self.logger = logger
#         self.level = level
#
#     def write(self, message):
#         if message != '\n':
#             self.logger.log(self.level, message)
#
#     def flush(self):
#         pass
#
# # 一份写文件 一份直接输出
# log = logging.getLogger()
# file_name = "./sflow_to_kafka.log"
# logformatter = logging.Formatter('%(asctime)s %(lineno)d [%(levelname)s] | %(message)s')
# loghandler = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
# loghandler.setFormatter(logformatter)
# loghandler.suffix = "%Y-%m-%d"
# log.addHandler(loghandler)
# log.setLevel(logging.)
#
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(logformatter)
# logging.getLogger('').addHandler(console)
# redirectStd = LoggerWriter(log, logging.INFO)
# sys.stderror = redirectStd
# sys.stdout = redirectStd

ip_proto_name = {0: 'ip',
                 1: 'icmp',
                 2: 'igmp',
                 3: 'ggp',
                 4: 'ipencap',
                 5: 'st',
                 6: 'tcp',
                 8: 'egp',
                 9: 'igp',
                 12: 'pup',
                 17: 'udp',
                 20: 'hmp',
                 22: 'xns-idp',
                 27: 'rdp',
                 29: 'iso-tp4',
                 36: 'xtp',
                 37: 'ddp',
                 38: 'idpr-cmtp',
                 41: 'ipv6',
                 43: 'ipv6-route',
                 44: 'ipv6-frag',
                 45: 'idrp',
                 46: 'rsvp',
                 47: 'gre',
                 50: 'esp',
                 51: 'ah',
                 57: 'skip',
                 58: 'ipv6-icmp',
                 59: 'ipv6-nonxt',
                 60: 'ipv6-opts',
                 73: 'rspf',
                 81: 'vmtp',
                 88: 'eigrp',
                 89: 'ospf',
                 93: 'ax.25',
                 94: 'ipip',
                 97: 'etherip',
                 98: 'encap',
                 103: 'pim',
                 108: 'ipcomp',
                 112: 'vrrp',
                 115: 'l2tp',
                 124: 'isis',
                 132: 'sctp',
                 133: 'fc',
                 136: 'udplite'}


def proto_to_name(i):
    return ip_proto_name[i]


def mac_(s_):
    l = s_[0:2] + ":" + s_[2:4] + ":" + s_[4:6] + ":" + s_[6:8] + ":" + s_[8:10] + ":" + s_[10:12]
    return l


# 因为python2的编码大坑引入的递归函数 json.loads产出的字典全变成Unicode了 Unicode直接查value是匹配不到的
def byteify(input_):
    if isinstance(input_, dict):
        return {byteify(key): byteify(value) for key, value in input_.iteritems()}
    elif isinstance(input_, list):
        return [byteify(element) for element in input_]
    elif isinstance(input_, unicode):
        return input_.encode('utf-8')
    else:
        return input_


class SflowListener(object):
    def __init__(self, port, kafka, topic, que):
        self.port = port
        self._flag = True
        self.kafka = kafka
        self.topic = topic
        self.que = que
        self.mode = "none"
        self.rule = {}
        self.log_producer = KafkaProducer(bootstrap_servers=KAFKA)
        self.filter_index = ["none", "agent", "input_port", "output_port", "src_mac", "dst_mac", "ethernet_type",
                             "in_vlan", "out_vlan", "src_ip", "dst_ip", "proto", "ip_tos", "ip_ttl", "src_port",
                             "dst_port", "tcp_flag", "packet_size", "ip_size", "sampling_rate"]

    def __flow_parse(self, gram):
        res = dict()
        res["time_stamp"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        res["agent"] = gram[1]
        res["input_port"] = gram[2]
        res["output_port"] = gram[3]
        res["src_mac"] = mac_(gram[4])
        res["dst_mac"] = mac_(gram[5])
        res["ethernet_type"] = gram[6]
        res["in_vlan"] = gram[7]
        res["out_vlan"] = gram[8]
        res["src_ip"] = gram[9]
        res["dst_ip"] = gram[10]
        if int(gram[11]) not in ip_proto_name:
            res["proto"] = gram[11]
        else:
            res["proto"] = proto_to_name(int(gram[11]))

        res["ip_tos"] = gram[12]
        res["ip_ttl"] = gram[13]
        res["src_port"] = gram[14]
        res["dst_port"] = gram[15]
        res["tcp_flag"] = gram[16]
        res["packet_size"] = gram[17]
        res["ip_size"] = gram[18]
        res["sampling_rate"] = gram[19]
        return res

    def __cntr_parse(self, gram):
        #   gram: typedef struct _SFLIf_counters {
        #   uint32_t ifIndex;
        #   uint32_t ifType;
        #   uint64_t ifSpeed;
        #   uint32_t ifDirection;        /* Derived from MAU MIB (RFC 2668)
        #                    0 = unknown, 1 = full-duplex,
        #                    2 = half-duplex, 3 = in, 4 = out */
        #   uint32_t ifStatus;           /* bit field with the following bits assigned:
        #                    bit 0 = ifAdminStatus (0 = down, 1 = up)
        #                    bit 1 = ifOperStatus (0 = down, 1 = up) */
        #   uint64_t ifInOctets;
        #   uint32_t ifInUcastPkts;
        #   uint32_t ifInMulticastPkts;
        #   uint32_t ifInBroadcastPkts;
        #   uint32_t ifInDiscards;
        #   uint32_t ifInErrors;
        #   uint32_t ifInUnknownProtos;
        #   uint64_t ifOutOctets;
        #   uint32_t ifOutUcastPkts;
        #   uint32_t ifOutMulticastPkts;
        #   uint32_t ifOutBroadcastPkts;
        #   uint32_t ifOutDiscards;
        #   uint32_t ifOutErrors;
        #   uint32_t ifPromiscuousMode;
        # } SFLIf_counters;
        # :return: FLOW gram dict

        res = dict()
        res["agent"] = gram[1]
        res["ifIndex"] = gram[2]
        res["ifType"] = gram[3]
        res["ifSpeed"] = gram[4]
        res["ifDirection"] = gram[5]
        res["ifStatus"] = gram[6]
        res["ifInOctets"] = gram[7]
        res["ifInUcastPkts"] = gram[8]
        res["ifInMulticastPkts"] = gram[9]
        res["ifInBroadcastPkts"] = gram[10]
        res["ifInDiscards"] = gram[11]
        res["ifInErrors"] = gram[12]
        res["ifInUnknownProtos"] = gram[13]
        res["ifOutOctets"] = gram[14]
        res["ifOutUcastPkts"] = gram[15]
        res["ifOutMulticastPkts"] = gram[16]
        res["ifOutBroadcastPkts"] = gram[17]
        res["ifOutDiscards"] = gram[18]
        res["ifOutErrors"] = gram[19]
        res["ifPromiscuousMode"] = gram[20]
        return res

    def send_kafka(self, res):
        try:
            producer = KafkaProducer(bootstrap_servers=self.kafka)
            producer.send(self.topic, json.dumps(res))
            producer.flush()
            producer.close()
        except Exception:
            pass

    def stop_listen(self):
        self._flag = False

    def start_listen(self):
        d = dict()
        d["cmd"] = "listen_start"
        d["type"] = "STATUS_OVS"
        d["message"] = {
            "ip": hostIP,
            "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        }
        self.log_producer.send(LOG_TOPIC, json.dumps(d))
        self.log_producer.flush()
        # 调用sflowtool
        handler = Popen('/usr/local/bin/sflowtool -p %s -l' % str(self.port),
                        stdout=PIPE, shell=True, stderr=PIPE)
        while self._flag:
            # if self.que is empty 在这判断是否队列空 如果非空设置模式和rule
            # print '\n\n', self.que.qsize()
            # print self.rule
            if self.que.empty() is False:
                self.rule = self.que.get()
                self.mode = self.rule["mode"]
                d = dict()
                d["cmd"] = "echo"
                d["type"] = "STATUS_OVS"
                d["message"] = {
                    "ip": hostIP,
                    "switch_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    "filter_cfg": json.dumps(self.rule)
                }
                self.log_producer.send(LOG_TOPIC, json.dumps(d))
                self.log_producer.flush()
                # print "change mode"
            gram = handler.stdout.readline().replace("\n", "").split(",")
            if gram[0] == 'FLOW':
                result = self.__flow_parse(gram)
                self.send_kafka(res=result)
            if gram[0] == 'CNTR':
                pass
                #     result = self._cntr_parse(gram)
                #     self.send_kafka(res=result)
        handler.kill()
        sys.exit(1)


# def mp_task(que):
#     error_msg = dict()
#     allow_rule = ["none", "agent", "input_port", "output_port", "src_mac", "dst_mac", "ethernet_type",
#                   "in_vlan", "out_vlan", "src_ip", "dst_ip", "proto", "ip_tos", "ip_ttl", "src_port",
#                   "dst_port", "tcp_flag", "packet_size", "ip_size", "sampling_rate"]
#     consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)
#     producer = KafkaProducer(bootstrap_servers=KAFKA)
#     log_pro = KafkaProducer(bootstrap_servers=KAFKA)
#     while True:
#         try:
#             jstr = next(consumer)
#             cfg = byteify(json.loads(jstr.value))
#             if cfg["evidence"] not in allow_rule or cfg["mode"] not in ["none", "filter"]:
#                 error_msg["cmd"] = "err_msg"
#                 error_msg["type"] = "STATUS_OVS"
#                 error_msg["message"] = {
#                     "err_host": hostIP,
#                     "err_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
#                     "err_info": "error config",
#                     "err_cfg": cfg
#                 }
#                 log_pro.send(LOG_TOPIC, json.dumps(error_msg))
#                 log_pro.flush()
#             if cfg["agent"] == hostIP:
#                 que.put(cfg)
#             else:
#                 producer.send(CONFIG_TOPIC, jstr)
#                 time.sleep(0.5)
#         except ValueError:
#             time.sleep(0.5)
#             continue


def heartbeat():
    d = dict()
    log_pro = KafkaProducer(bootstrap_servers=KAFKA)
    while True:
        d["cmd"] = "heartbeats"
        d["type"] = "STATUS_OVS"
        d["message"] = {
            "ip": hostIP,
            "heart_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        }
        log_pro.send(LOG_TOPIC, json.dumps(d))
        log_pro.flush()
        time.sleep(20)


if __name__ == '__main__':
    q = mp.Queue(4)
    s = SflowListener(port=SFLOW_PORT, kafka=KAFKA, topic=PRODUCER_TOPIC, que=q)
    # p1 = mp.Process(target=mp_task, args=(q,))
    hb = mp.Process(target=heartbeat)
    # p1.daemon = True
    hb.daemon = True
    # p1.start()
    hb.start()
    s.start_listen()
    # p1.join()
    hb.join()
