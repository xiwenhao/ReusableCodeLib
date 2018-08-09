#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_dp_sflow_server.py
# @time: 2017/9/5 0005 上午 8:15
# @desc: 通过kafka下发的配置部署sflow

# message = '{"id_code": "1","network_card": "em4","sample_rate": "2",
#             "monitor_ip": "192.168.100.16", "monitor_port": "6343"}'
# id_code 是命令唯一编号 作为区分连续的命令的失败或者成功
#

import signal
import json
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import subprocess
import multiprocessing as mp
from kafka import KafkaConsumer, KafkaProducer
import time


KAFKA = "192.168.100.15:9092"
# 获取配置topic
CONSUMER_TOPIC = "SFLOW_CONFIG"

# 部署结果topic
DEPLOY_RESULT_TOPIC = "OPERATION"

# beats topic
LOG_TOPIC = "OPERATION"

CONSUMER_GROUP = "sflow_group"

deploy_info = mp.Queue(2)


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

# log = logging.getLogger()
# file_name = "./deploy_nf.log"
# logformatter = logging.Formatter('%(asctime)s %(lineno)d [%(levelname)s] | %(message)s')
# loghandler = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
# loghandler.setFormatter(logformatter)
# loghandler.suffix = "%Y-%m-%d"
# log.addHandler(loghandler)
# log.setLevel(logging.INFO)
#
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(logformatter)
# logging.getLogger('').addHandler(console)
# redirectStd = LoggerWriter(log, logging.INFO)
# sys.stderror = redirectStd
# sys.stdout = redirectStd


# 从kafka消费数据放入队列
def get_config(que):
    # consumer = KafkaConsumer(CONSUMER_TOPIC, groupid=CONSUMER_GROUP, bootstrap_servers=KAFKA)
    consumer = KafkaConsumer(CONSUMER_TOPIC, bootstrap_servers=KAFKA)
    log_producer = KafkaProducer(bootstrap_servers=KAFKA)
    hostIP = socket.gethostbyname(socket.gethostname())
    for message in consumer:
        if message is not None:
            try:
                msg = message.value
                d = {"cmd": "echo",
                     "type": "SFLOW_CONFIG_SERVER",
                     "message": {
                         "ip": hostIP,
                         "sflow_config": msg,
                         "time": hostTIME
                     }
                     }
                log_producer.send(LOG_TOPIC, json.dumps(d))
                que.put(json.loads(msg))
            except Exception:
                pass
            finally:
                time.sleep(0.1)


#  根据解析的json部署NF，返回uuid和结果
def deploy_sflow(info):
    match_success = False
    log_producer = KafkaProducer(bootstrap_servers=KAFKA)
    hostIP = socket.gethostbyname(socket.gethostname())
    time.sleep(0.1)
    while True:
        if info.empty() is not True:
            cfg_info = info.get()
            ret = os.popen('ovs-vsctl show').readlines()
            # ret[0] br uuid
            # ret[-1] ovs version
            brlen = len(ret)
            ethx = cfg_info["network_card"]
            # 控制匹配次数 如果匹配不到返回fail信息
            j = 0
            for i in ret:
                j += 1
                i = i.replace('\n', '').strip()
                # i是ovs-vsctl show的每一行
                if ethx in i and "no row" not in i:
                    match_success = True
            if match_success is True:
                cmd = 'ovs-vsctl -- --id=@sflow create sflow agent={network_card} \
                 target=\"{monitor_ip}:{monitor_port}\" header=64 sampling={sample_rate} \
                 polling=3 -- set bridge br-int sflow=@sflow'.format(
                    network_card=cfg_info["network_card"], monitor_ip=cfg_info["monitor_ip"],
                    monitor_port=cfg_info["monitor_port"], sample_rate=cfg_info["sample_rate"])
                time.sleep(0.1)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                r = str(p.stdout.readlines())
                # 返回结果r ['49bce471-bf23-4754-a69e-b27618e13e2b\n']
                br_uuid = r[2:-4]
                p.kill()
                # 如果br_name不是已有的网桥， r="[]" 长度2的字符串
                if len(r) != 2:
                    res = {"cmd": "result",
                           "type": "SFLOW_CONFIG_SERVER",
                           "message": {
                               "ip": hostIP,
                               "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                               "sflow_config": msg,
                               "time": hostTIME,
                               "result": "success",
                               "cmd_id": cfg_info["id_code"],
                               "uuid": br_uuid
                           }
                           }
                    log_producer.send(LOG_TOPIC, json.dumps(res))

                else:
                    res = {"cmd": "result",
                           "type": "SFLOW_CONFIG_SERVER",
                           "message": {
                               "ip": hostIP,
                               "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                               "sflow_config": msg,
                               "time": hostTIME,
                               "result": "fail",
                               "cmd_id": cfg_info["id_code"],
                               "uuid": "NIC not found"
                           }
                           }
                    log_producer.send(LOG_TOPIC, json.dumps(res))
                    continue
            elif j == brlen and match_success is False:
                res = {"cmd": "result",
                       "type": "SFLOW_CONFIG_SERVER",
                       "message": {
                           "ip": hostIP,
                           "start_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                           "sflow_config": msg,
                           "time": hostTIME,
                           "result": "fail",
                           "cmd_id": cfg_info["id_code"],
                           "uuid": "NIC not found"
                       }
                       }
                log_producer.send(LOG_TOPIC, json.dumps(res))
                continue
        else:
            time.sleep(0.5)
            continue


def beats():
    log_producer = KafkaProducer(bootstrap_servers=KAFKA)
    while True:
        beat = {"cmd": "heartbeats",
                "type": "SFLOW_SERVER",
                "message": {
                    "ip": hostIP,
                    "heart_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                }
                }
        log_producer.send(LOG_TOPIC, json.dumps(beat))
        time.sleep(20)


if __name__ == "__main__":
    p1 = mp.Process(target=get_config, args=(deploy_info, ))
    p2 = mp.Process(target=deploy_netflow, args=(deploy_info, deploy_result))
    p3 = mp.Process(target=beats())
    # 设置daemon进程，随主进程结束而结束
    p1.daemon = True
    p2.daemon = True
    p3.daemon = True
    p1.start()
    p2.start()
    p3.start()
    time.sleep(0.1)
    p1.join()
    p2.join()
    p3.join()
