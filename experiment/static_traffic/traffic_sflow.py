#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: traffic_sflow.py
# @time: 2017/11/29 0029 下午 4:57
# @author: xwh
# @desc: sflow v2.1

from subprocess import Popen, PIPE
from kafka import KafkaProducer, KafkaConsumer
import threading as th
from queue import Queue
from logging.handlers import TimedRotatingFileHandler
from queue import Empty
from socket import gethostname, gethostbyname
import logging
import ConfigParser
import json
import time
import re


log = logging.getLogger()
hostIP = gethostbyname(gethostname())


def initLog():
    global log
    file_name = "traffic_sflow.log"
    logformatter = logging.Formatter('%(asctime)s [%(levelname)s][%(lineno)d][%(thread)d] |%(message)s')
    loghandle = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
    loghandle.setFormatter(logformatter)
    loghandle.suffix = '%Y-%m-%d'
    log.addHandler(loghandle)
    # DEBUG < INFO < WARNING < ERROR < CRITICAL
    log.setLevel(logging.WARNING)

initLog()

iniFilePath = "./conf.ini"
conf = ConfigParser.ConfigParser()
with open(iniFilePath, "r") as fp:
    conf.readfp(fp)
    KAFKA = conf.get("sflow_cfg", "KAFKA").split(",")
    PRODUCER_TOPIC = conf.get("sflow_cfg", "PRODUCER_TOPIC")
    CONFIG_TOPIC = hostIP + conf.get("sflow_cfg", "CONFIG_TOPIC")
    LOG_TOPIC = conf.get("sflow_cfg", "LOG_TOPIC")
    SFLOW_PORT = conf.get("sflow_cfg", "SFLOW_PORT")
    REPORT_INTERVAL = int(conf.get("sflow_cfg", "REPORT_INTERVAL"))
    log.warning("start args " + str([KAFKA, PRODUCER_TOPIC, CONFIG_TOPIC, LOG_TOPIC, SFLOW_PORT, REPORT_INTERVAL]))


def _flow_parse(gram):
    '''
    key = gram_dict["src_mac"] + "#" + gram_dict["dst_mac"] + "#" + gram_dict["src_ip"] + "#" + \
    gram_dict["dst_ip"] + "#" + gram_dict["src_port"] + "#" + gram_dict["dst_port"] + "#" + \
    gram_dict["in_vlan"] + "#" + gram_dict["out_vlan"] + "#" + gram_dict["proto"]
    '''
    res = dict()
    res["agent"] = gram[1]
    # res["input_port"] = gram[2]
    # res["output_port"] = gram[3]
    res["src_mac"] = gram[4]
    res["dst_mac"] = gram[5]
    res["ethernet_type"] = gram[6]
    res["in_vlan"] = gram[7]
    res["out_vlan"] = gram[8]
    res["src_ip"] = gram[9]
    res["dst_ip"] = gram[10]
    res["proto"] = gram[11]
    # res["ip_tos"] = gram[12]
    # res["ip_ttl"] = gram[13]
    res["src_port"] = gram[14]
    res["dst_port"] = gram[15]
    # res["tcp_flag"] = gram[16]
    res["packet_size"] = int(gram[17])
    # res["ip_size"] = gram[18]
    # res["sampling_rate"] = gram[19]
    return res


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def fillResultDictProcess(mp_lock, gram_dict_que, stop_flag_que, cnt_mp_dict):
    log.warning("fillResultDictProcess init OK.")
    while stop_flag_que.empty():
        try:
            gram_dict = gram_dict_que.get(timeout=5)

            key = gram_dict["src_mac"] + "#" + gram_dict["dst_mac"] + "#" + gram_dict["src_ip"] + "#" + \
                gram_dict["dst_ip"] + "#" + gram_dict["src_port"] + "#" + gram_dict["dst_port"] + "#" + \
                gram_dict["in_vlan"] + "#" + gram_dict["out_vlan"] + "#" + gram_dict["proto"]
            mp_lock.acquire()
            key_set = set(cnt_mp_dict.keys())
            if key in key_set:
                cnt_mp_dict[key]["packet_size"] += gram_dict["packet_size"]
            else:
                cnt_mp_dict[key] = gram_dict
            mp_lock.release()
        except Empty:
            continue
    log.warning("fill result dict Process quit!")


def ageingResultDictProcess(stop_flag_que, mp_lock, cnt_mp_dict, ageing_time, send_pro_kafka_que):
    '''
    :param stop_flag_que: 多进程停止标志队列(非空时全部进程退出)
    :param mp_lock: 用来对多进程字典上锁
    :param cnt_mp_dict:真正用来计算mac的流量的字典
    :param ageing_time:老化时间
    :param send_pro_kafka_que:发送到正常结果Topic的kafka队列
    :return: None
    '''
    log.warning("ageingResultDictProcess init OK!")
    time.sleep(0.3)
    temp = dict()
    temp["traffic_info"] = dict()
    while stop_flag_que.empty():
        temp["report_interval"] = ageing_time
        # if len(cnt_mp_dict) < report_interval:
        if cnt_mp_dict["time"] > time.time() - ageing_time:
            time.sleep(0.001)
            continue
        else:
            mp_lock.acquire()
            for k, v in cnt_mp_dict.items():
                temp["traffic_info"][k] = v
            temp["traffic_info"].pop("time")
            # send kafka
            send_pro_kafka_que.put(temp)
            log.warning("send a result to kafka producer topic")
            temp.clear()
            cnt_mp_dict.clear()
            temp["key"] = hostIP
            temp["traffic_info"] = {}
            cnt_mp_dict["time"] = time.time()
            mp_lock.release()
    log.warning("ageingResultDictProcess quit!")


def testMac(mac_str):
    if len(mac_str) != 17:
        return False
    if re.match("([A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}", mac_str) is None:
        return False
    return True


def callSflowToolProcess(gram_dict_que, stop_flag_que, rule_mp_dict):
    '''
    :param gram_dict_que: 未解析的sflowtool的行缓冲字符串
    :param stop_flag_que: 多进程停止标志
    :param rule_mp_dict: 用字典的key当做白名单set使用 value无意义
    :return: None
    '''
    log.warning("callSflowToolProcess init OK!")
    handler = Popen("/usr/local/bin/sflowtool -p %s -l" % SFLOW_PORT, shell=True, stdout=PIPE, stderr=PIPE)
    out = handler.stdout.readline()
    if len(out) == 0:
        log.error("call sflowtool error! \n")
        stop_flag_que.put("stop")
        time.sleep(0.2)
    log.warning("sflowtool init OK")
    while stop_flag_que.empty():
        gram = handler.stdout.readline().split(",")
        if "CNTR" in gram:
            continue
        # update rule set
        rule = rule_mp_dict.keys()
        # 切换白名单或者全部统计
        if gram[4] not in rule and gram[5] not in rule:
            # pass
            continue
        gram_dict_que.put(_flow_parse(gram))

        load = gram_dict_que.qsize()
        if load > 64:
            # 如果处理速度慢 在队列负载超过二分之一队列长度时警告(正常速度队列负载不会超过10)
            log.warning("high load, current queue load %s / 128" % load)
    handler.kill()
    log.warning("callSflowToolProcess quit!")


def sendToKafkaProTopic(send_pro_kafka_que, stop_flag_que):
    log.warning("sendToKafkaProTopic init OK!")
    while stop_flag_que.empty():
        producer = KafkaProducer(bootstrap_servers=KAFKA)
        while stop_flag_que.empty():
            try:
                msg = send_pro_kafka_que.get(timeout=5)
                if len(msg) == 0:
                    continue
                msg["time"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                producer.send(PRODUCER_TOPIC, key=hostIP, value=json.dumps(msg))
            except Empty:
                break
            except Exception as e:
                log.error("producer error! try to rebuild producer detail: %s" % e.message)
                break
        producer.close()
    log.warning("sendToKafkaProTopic quit!")


def sendToKafkaLogTopic(send_log_kafka_que, stop_flag_que):
    log.warning("sendToKafkaLogTopic init OK!")
    while stop_flag_que.empty():
        producer = KafkaProducer(bootstrap_servers=KAFKA)
        while stop_flag_que.empty():
            try:
                msg = send_log_kafka_que.get(timeout=5)
                producer.send(LOG_TOPIC, key=hostIP, value=json.dumps(msg))
            except Empty:
                break
            except Exception as e:
                log.error("log_producer error! try to rebuild log_pro detail: %s" % e.message)
                break
        producer.close()
    log.warning("sendToKafkaLogTopic quit!")


def recvConfigFromKafkaProcess(stop_flag_que, rule_mp_dict, send_log_kafka_que):
    while stop_flag_que.empty():
        consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)
        log.warning("recvConfigFromKafkaProcess init OK.")
        error_mac_dict = dict()
        while stop_flag_que.empty():
            try:
                msg = next(consumer)
                cfg = byteify(json.loads(msg.value))
                log.warning("consumer get a msg: %s" % str(msg))

                send_log_kafka_que.put(msgGen("echo", cfg))
                error_mac_dict.clear()
                if cfg["operation"] == "add":
                    _mac_list = cfg["mac_list"].replace(" ", "").split(",")
                    for mac in _mac_list:
                        if testMac(mac):
                            rule_mp_dict[mac.replace(":", "")] = 1
                            send_log_kafka_que.put(msgGen("add_success", {mac: 1}))
                            log.warning("add a key into rule: %s" % mac)
                        else:
                            log.error("bad mac string %s" % mac)
                            error_mac_dict[mac] = 0
                    if len(error_mac_dict) != 0:
                        send_log_kafka_que.put(msgGen("add_fail", msg_info_dict=error_mac_dict))
                    error_mac_dict.clear()
                    continue

                if cfg["operation"] == "sub":
                    _mac_list = cfg["mac_list"].replace(" ", "").split(",")
                    for mac in _mac_list:
                        try:
                            rule_mp_dict.pop(mac.replace(":", ""))
                            log.warning("remove a key from rule: %s" % mac)
                            send_log_kafka_que.put(msgGen("sub_success", {mac: 1}))
                            continue
                        except KeyError:
                            log.error("try to remove a non-existent key! %s" % mac)
                            error_mac_dict[mac] = 0
                    if len(error_mac_dict) != 0:
                        send_log_kafka_que.put(msgGen("sub_fail", msg_info_dict=error_mac_dict))
                    error_mac_dict.clear()
                    continue

                if cfg["operation"] == "query":
                    send_log_kafka_que.put(msgGen("query", rule_mp_dict))
                    log.warning("query rule : %s" % str(rule_mp_dict.keys()))
                    continue

                if cfg["operation"] == "clear":
                    log.warning("clear rule: %s" % str(rule_mp_dict.keys()))
                    rule_mp_dict.clear()
                    continue
                if cfg["operation"] == "stop":
                    stop_flag_que.put("stop")
                    time.sleep(0.2)
                    log.warning("sflow_v2.1 quit!")

            except KeyError:
                log.error("error config from kafka: KeyError!")
                continue
            except Exception as e:
                log.error("recv cfg process error : %s" % e)
                break
        consumer.close()
    log.warning("recvConfigFromKafkaProcess quit!")


def msgGen(msg_type, msg_info_dict):
    '''
    :param msg_type: 生成消息类型
    :param msg_info_dict: 更多的信息补充
    :return: 如果参数不符合期望 返回 False
    '''
    # if isinstance(msg_info_dict, dict):
    #     print 11111
    #     return False

    if msg_type == "echo":
        return {
            "cmd": "echo",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
             "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
             "cfg": msg_info_dict
            }
        }
    if msg_type == "add_success":
        return {
            "cmd": "add_success",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "current_add": msg_info_dict.keys()[0]
            }
        }
    if msg_type == "sub_success":
        return {
            "cmd": "sub_success",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "current_sub": msg_info_dict.keys()[0]
            }
        }
    if msg_type == "sub_fail":
        return {
            "cmd": "sub_fail",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "fail_list": str(msg_info_dict.keys())[1:-1].replace("'", "").replace(" ", "")
            }
        }
    if msg_type == "add_fail":
        return {
            "cmd": "add_fail",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
                "time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "fail_list": str(msg_info_dict.keys())[1:-1].replace("'", "").replace(" ", "")
            }
        }
    if msg_type == "heartBeat":
        return {
            "cmd": "heartbeats",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
                "heart_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "current_list": str(msg_info_dict.keys())[1:-1].replace("'", "").replace(" ", "")
            }
        }
    if msg_type == "query":
        return {
            "cmd": "query",
            "type": "STATUS_OVS",
            "hostIP": hostIP,
            "message": {
                "query_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                "current_list": str(msg_info_dict.keys())[1:-1].replace("'", "").replace(" ", "")
            }
        }
    return False


def heartBeatProcess(stop_flag_que, send_log_kafka_que, rule_mp_dict):
    log.warning("heartBeatProcess init OK!")
    temp = dict()
    while stop_flag_que.empty():
        time.sleep(5)
        if not stop_flag_que.empty():
            break
        time.sleep(5)
        if not stop_flag_que.empty():
            break
        # 心跳前更新, mp_dict对于json序列化可能会出错
        for k, v in rule_mp_dict.items():
            temp[k] = v
        send_log_kafka_que.put(msgGen("heartBeat", temp))
        temp.clear()
    log.warning("heartBeatProcess quit!")


if __name__ == '__main__':
    log.warning("\n---------------------------------new start-----------------------------------\n")
    gram_dict_que = Queue(128)
    stop_flag_que = Queue(1)
    send_pro_kafka_que = Queue(10)
    send_log_kafka_que = Queue(5)
    rule_mp_dict = dict()
    mp_lock = th.Lock()
    cnt_mp_dict = dict()
    cnt_mp_dict["time"] = time.time()
    ageing_time = REPORT_INTERVAL

    p1 = th.Thread(name="callSflowToolProcess", target=callSflowToolProcess, args=(
        gram_dict_que, stop_flag_que, rule_mp_dict))
    p2 = th.Thread(name="fillResultDictProcess", target=fillResultDictProcess, args=(
        mp_lock, gram_dict_que, stop_flag_que, cnt_mp_dict))
    p3 = th.Thread(name="ageingResultDictProcess", target=ageingResultDictProcess, args=(
        stop_flag_que, mp_lock, cnt_mp_dict, ageing_time, send_pro_kafka_que))
    p4 = th.Thread(name="sendToKafkaProTopic", target=sendToKafkaProTopic, args=(send_pro_kafka_que, stop_flag_que))
    p5 = th.Thread(name="sendToKafkaLogTopic", target=sendToKafkaLogTopic, args=(send_log_kafka_que, stop_flag_que))
    p6 = th.Thread(name="recvConfigFromKafkaProcess", target=recvConfigFromKafkaProcess, args=(
        stop_flag_que, rule_mp_dict, send_log_kafka_que))
    p7 = th.Thread(name="heartBeatProcess", target=heartBeatProcess, args=(
        stop_flag_que, send_log_kafka_que, rule_mp_dict))
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
