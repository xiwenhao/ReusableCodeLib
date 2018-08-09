#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: ageing_base_module.py
# @time: 2017/11/21 0021 上午 8:44
# @author: xwh
# @desc:

import multiprocessing as mp
import time

def th1(mp_dict, mp_lock, stop_flag):
    i = 0
    while not stop_flag:
        i += 1
        mp_lock.acquire()
        mp_dict["time_%s" % i] = i
        print "filling dict"
        mp_lock.release()
        time.sleep(1)


def th2(mp_dict, mp_lock, stop_flag):
    while not stop_flag:
        if mp_dict["time"] < time.time() - 5.1:
            mp_lock.acquire()
            print mp_dict
            mp_dict.clear()
            mp_dict["time"] = time.time()
            mp_lock.release()
        else:
            continue
    pass


if __name__ == '__main__':
    manager = mp.Manager()
    mp_dict = manager.dict()
    mp_dict["time"] = time.time()
    mp_dict["flag"] = 0
    mp_lock = mp.Lock()
    stop_flag = mp.Value("b")
    stop_flag = 0
    p1 = mp.Process(target=th1, args=(mp_dict, mp_lock, stop_flag))
    p2 = mp.Process(target=th2, args=(mp_dict, mp_lock, stop_flag))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


'''
from subprocess import Popen, PIPE
from kafka import KafkaProducer, KafkaConsumer
import multiprocessing as mp
import threading as th
from logging.handlers import TimedRotatingFileHandler
import socket
import logging
import json
import time
import sys

# ----------------------------------宏定义-----------------------------------#
# kafka服务器地址
KAFKA = "192.168.100.15:9092"
PRODUCER_TOPIC = "STATUS_OVS"

# 获取配置topic
hostIP = socket.gethostbyname(socket.gethostname())
if len(sys.argv) == 1:
    CONFIG_TOPIC = hostIP + "_SFLOW_FILTER_CONFIG"
else:
    CONFIG_TOPIC = sys.argv[1]

# 运维topic
LOG_TOPIC = "OPERATION"
# 默认sflow的端口
SFLOW_PORT = 6343
SUPPORT_OPERATION = ['add', 'sub', 'clear', 'query']

# ----------------------------------end宏定义--------------------------------#

log = logging.getLogger()


def initLog():
    import sys
    global log
    file_name = sys.argv[0][0:-3] + "_log.log"
    logformatter = logging.Formatter('%(asctime)s [%(levelname)s][%(lineno)d][%(thread)d] |%(message)s')
    loghandle = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
    loghandle.setFormatter(logformatter)
    loghandle.suffix = '%Y-%m-%d'
    log.addHandler(loghandle)
    # DEBUG < INFO < WARNING < ERROR < CRITICAL
    log.setLevel(logging.WARNING)

initLog()


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


def mac2string(s_):
    l = s_[0:2] + ":" + s_[2:4] + ":" + s_[4:6] + ":" + s_[6:8] + ":" + s_[8:10] + ":" + s_[10:12]
    return l


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def _flow_parse(gram):
    res = dict()
    res["time_stamp"] = str(time.time())
    res["agent"] = gram[1]
    res["input_port"] = gram[2]
    res["output_port"] = gram[3]
    res["src_mac"] = mac2string(gram[4])
    res["dst_mac"] = mac2string(gram[5])
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


def callSflowToolProcess(parsed_gram_que, stop_flag, rule_op_dict_que, log_str_que):
    # get gram from sflowtool
    handler = Popen('sflowtool -p %s -l|grep FLOW' % SFLOW_PORT, stdout=PIPE, shell=True, stderr=PIPE)
    rule = set()
    logging.warning("callSflowToolProcess init OK..")
    while not stop_flag:
        try:
            # modify rule_set
            if not rule_op_dict_que.empty():
                cmd = rule_op_dict_que.get()
                if cmd["operation"] == "add":
                    rule.add(cmd["key"])
                    logging.warning("put a value into rule_set.")
                if cmd["operation"] == "sub":
                    rule.remove(cmd["key"])
                    logging.warning("remove a value from rule_set.")
                if cmd["operation"] == "clear":
                    rule.clear()
                    logging.warning("clear the rule_set.")
                if cmd["operation"] == "query":
                    log_str_que.put(msgGen("query", rule_str=str(rule)))
                continue

            line_buffer = handler.stdout.readline()
            # if "FLOW" not in line_buffer:
            #     continue
            temp_dict = _flow_parse(line_buffer.replace("\n", "").split(","))
            # if not in rule_set: ignore this loop
            if temp_dict["src_mac"] in rule or temp_dict["dst_mac"] in rule:
                parsed_gram_que.put(temp_dict)
        except AttributeError:
            logging.error("get type_error from rule_op_dict_que! \n")
            continue
        except KeyError:
            logging.error("try to remove a non-existent value from rule set! \n")
            continue
    logging.warning("callSflowToolProcess quit!\n")
    handler.kill()


def getConfigFromKafkaProcess(stop_flag, rule_op_dict_que):
    logging.warning("getConfigFromKafkaProcess init OK...")
    while not stop_flag:
        consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)
        while not stop_flag:
            try:
                msg = next(consumer)
                cfg_from_kafka_dict = byteify(json.loads(msg.value))
                logging.warning("get a cfg from kafka")
                if testConfigOperation(cfg_from_kafka_dict):
                    rule_op_dict_que.put(cfg_from_kafka_dict)
                else:
                    logging.warning("error config_msg from kafka!\n")
                    continue
            except Exception as e:
                logging.warning("kafka consumer error : " + e.message)
                break
    logging.warning("Get Config Process Quit! \n")


def testConfigOperation(cfg_dict):
    # ensure msg is right
    if cfg_dict["operation"] in SUPPORT_OPERATION:
        return True
    else:
        return False


def makeResultDictProcess(parsed_gram_que, cnt_mp_dict, stop_flag, lock):
    #  filling dict
    # parsed_gram is dict
    logging.warning("makeResultDictProcess init OK...")
    while not stop_flag:
        lock.acquire()
        logging.warning("makeResultDictProcess acquire lock")
        parsed_gram = parsed_gram_que.get()
        print parsed_gram
        print parsed_gram_que.qsize()
        logging.warning("current gram load : %s / 128" % parsed_gram_que.qsize())
        keys_set = cnt_mp_dict.keys()
        if parsed_gram["src_mac"] not in keys_set:
            cnt_mp_dict["src_mac_"+parsed_gram["src_mac"]] = parsed_gram["packet_size"]
            cnt_mp_dict["dst_mac_"+parsed_gram["dst_mac"]] = parsed_gram["packet_size"]
        else:
            cnt_mp_dict["src_mac_"+parsed_gram["src_mac"]] += int(parsed_gram["packet_size"])
            cnt_mp_dict["dst_mac_"+parsed_gram["dst_mac"]] += int(parsed_gram["packet_size"])

        if parsed_gram["dst_mac"] not in keys_set:
            cnt_mp_dict["dst_mac_"+parsed_gram["dst_mac"]] = parsed_gram["packet_size"]
        else:
            cnt_mp_dict["dst_mac_"+parsed_gram["dst_mac"]] += int(parsed_gram["packet_size"])
        lock.release()
        logging.warning("makeResultDictProcess release lock")
    logging.warning("Make Result Dict Process Quit! \n")


def ageingProcess(stop_flag, cnt_mp_dict, mp_lock):



def send2ResultKafkaProcess(cnt_mp_dict, stop_flag, ageing_time, lock):
    # FIXME lock
    # send kafka and ageing dict
    logging.warning("send2ResultKafkaProcess init OK...")
    temp_dict = dict()
    while not stop_flag:
        producer = KafkaProducer(bootstrap_servers=KAFKA)
        while not stop_flag:
            try:
                producer.send(PRODUCER_TOPIC, )

    logging.warning("Send Result Process Quit ! \n")


def send2OperationKafkaProcess(log_str_que, stop_flag):
    logging.warning("send2OperationKafkaProcess init OK...")
    while not stop_flag:
        log_producer = KafkaProducer(bootstrap_servers=KAFKA)
        while not stop_flag:
            try:
                log_producer.send(LOG_TOPIC, json.dumps(log_str_que.get()))
            except Exception as e:
                logging.warning("log_producer error! %s" % e.message)
                break
    logging.warning("Send Log Process Quit!\n")


def msgGen(msg_type, **kwargs):
    if msg_type == "heartbeat":
        return {
            "cmd": "heartbeats",
            "type": "STATUS_OVS",
            "message": {
                "ip": hostIP,
                "heart_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }
        }

    elif msg_type == "echo":
        return {
            "cmd": "echo",
            "type": "STATUS_OVS",
            "message": {
                "ip": hostIP,
                "switch_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "cfg": kwargs["cfg"]
            }
        }

    elif msg_type == "start":
        return {
            "cmd": "listen_start",
            "type": "STATUS_OVS",
            "message": {
                "ip": hostIP,
                "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            }
        }

    elif msg_type == "error_cmd":
        return {
            "cmd": "error_cmd",
            "type": "STATUS_OVS",
            "message": {
                "ip": hostIP,
                "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "error_message": "KeyError",
                "error_cfg": kwargs["error_cfg"]
            }
        }

    elif msg_type == "query":
        return {
            "cmd": "search",
            "type": "STATUS_OVS",
            "message": {
                "ip": hostIP,
                "search_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "current_rule": kwargs["rule_str"]
            }
        }

    elif msg_type == "result":
        return {
            "cmd": "result_in_%s" % kwargs["ageing_time"],
            "type": "STATUS_OVS",
            "message": {
                "ip": hostIP,
                "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "result": kwargs["result_str"]
            }
        }
    else:
        return {}


def heartbeatProcess(stop_flag):
    logging.warning("heartbeatProcess init OK..")
    while not stop_flag:
        hb = KafkaProducer(bootstrap_servers=KAFKA)
        while not stop_flag:
            try:
                hb.send(LOG_TOPIC, json.dumps(msgGen("heartbeat")))
                time.sleep(5)
            except Exception as e:
                logging.warning("heartbeatProcess producer error! %s" % e.message)
                break


if __name__ == '__main__':
    logging.warning("\n\n----------------sflow_start----------------------")
    parsed_gram_que = mp.Queue(128)
    # mp boolean stop_flag
    stop_flag = mp.Value("b")
    stop_flag = False
    result_dict_que = mp.Queue(4)
    rule_op_dict_que = mp.Queue(4)
    manager = mp.Manager()
    cnt_mp_dict = manager.dict()
    cnt_mp_dict["time"] = time.time()
    ageing_time = mp.Value("b")
    ageing_time = 3
    lock = th.Lock()
    log_str_que = mp.Queue(4)

    p1 = mp.Process(name="callSflowToolProcess", target=callSflowToolProcess, args=(
        parsed_gram_que, stop_flag, rule_op_dict_que, log_str_que))
    p2 = mp.Process(name="getConfigFromKafkaProcess", target=getConfigFromKafkaProcess, args=(
        stop_flag, rule_op_dict_que))
    p3 = th.Thread(name="makeResultDictProcess", target=makeResultDictProcess, args=(
        parsed_gram_que, cnt_mp_dict, stop_flag, lock))
    p4 = th.Thread(name="send2ResultKafkaProcess", target=send2ResultKafkaProcess, args=(
        cnt_mp_dict, stop_flag, ageing_time, lock))
    p5 = mp.Process(name="send2OperationKafkaProcess", target=send2OperationKafkaProcess, args=(
        log_str_que, stop_flag))
    p6 = mp.Process(name="heartbeatProcess", target=heartbeatProcess, args=(stop_flag,))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()

    p1.setDaemon = True
    p2.setDaemon = True
    p3.setDaemon = True
    p4.setDaemon = True
    p5.setDaemon = True
    p6.setDaemon = True

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    logging.warning("---------------------sflow_end----------------------\n\n")

'''