#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_dp_netflow_server.py
# @time: 2017/8/23 0023 上午 10:04
# @desc: 通过kafka下发的配置部署sflow
# kafka python 不消费历史数据 所以必须先运行话题消息消费者 再运行生产者
#        消费时阻塞
# 进程p1 消费kafka放入队列， 进程p2 部署，把结果放入队列   主进程负责信号退出清除nf和把部署结果生产到kafka

import signal
import json
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import subprocess
import multiprocessing as mp
from kafka import KafkaConsumer, KafkaProducer
from time import sleep


KAFKA = "192.168.100.15:9092"
# 获取配置topic
CONSUMER_TOPIC = "xwh-consumer"

# 部署结果topic
DEPLOY_RESULT_TOPIC = "OPERATION"

# beats topic
BEATS_TOPIC = "OPERATION"

CONSUMER_GROUP = "simplegroup"

deploy_info = mp.Queue(8)
deploy_result = mp.Queue(8)

# 退出时需要清除的br列表
br_list = []

# message = '{"br_name": "br0", "engine_id": "1", "monitor_ip": "192.168.100.16", "monitor_port": "2055"}'

# result = '{"status": "success or fail", "br_name": "br0", "result": "uuid or br could found"}'


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
file_name = "./deploy_nf.log"
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


def send(topic, msg):
    log_producer.send(topic=topic, value=str(msg).encode('utf-8'))


# 从kafka消费数据放入队列
def get_config(que):
    # consumer = KafkaConsumer(CONSUMER_TOPIC, groupid=CONSUMER_GROUP, bootstrap_servers=KAFKA)
    consumer = KafkaConsumer(CONSUMER_TOPIC, bootstrap_servers=KAFKA)
    logging.info('waitint kafka producer ...\n')
    for message in consumer:
        if message is not None:
            try:
                msg = json.loads(message.value)
                que.put(msg)
                send(BEATS_TOPIC, "get config_msg from kafka...")
                logging.info("get config_msg from kafka...")
            except ValueError as e:
                logging.error(e)
                send(BEATS_TOPIC, e)
            except Exception as e:
                logging.error(e)
                send(BEATS_TOPIC, e)
            finally:
                sleep(0.1)


#  根据解析的json部署NF，返回uuid和结果
def deploy_netflow(info, result):
    match_success = False
    res = {}
    sleep(0.1)
    while True:
        if info.empty is not True:
            cfg_info = info.get()
            ret = os.popen('ovs-vsctl show').readlines()
            # ret[0] br uuid
            # ret[-1] ovs version
            brlen = len(ret)

            # 控制匹配次数 如果匹配不到返回fail信息
            j = 0
            br_name = str(cfg_info["br_name"]).encode('utf-8')
            send(BEATS_TOPIC, "start match br...")
            logging.info("start match br...")
            for i in ret:
                j += 1
                i = i.replace('\n', '').strip()
                # i是ovs-vsctl show的每一行
                if br_name in i and "no row" not in i:
                    match_success = True
            if match_success is True:
                logging.info("match br success")
                # active-timeout 控制数据返回间隔
                cmd = '/usr/bin/ovs-vsctl -- --id=@nf create NetFlow targets=\\"%s:%s\\" active-timeout=3 ' \
                      'engine-id=%s -- set Bridge %s netflow=@nf' % (cfg_info["monitor_ip"], cfg_info["monitor_port"],
                                                                     cfg_info["engine_id"], cfg_info["br_name"])
                send(BEATS_TOPIC, "exec %s" % cmd)
                sleep(0.1)
                logging.info("start deploy...")
                send(BEATS_TOPIC, "start deploy...")
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                r = str(p.stdout.readlines())
                # 返回结果r ['49bce471-bf23-4754-a69e-b27618e13e2b\n']
                br_uuid = r[2:-4]
                p.kill()
                # 如果br_name不是已有的网桥， r="[]" 长度2的字符串
                if len(r) != 2:
                    res["br_name"] = cfg_info["br_name"]
                    res["result"] = "%s" % br_uuid
                    res["status"] = "success"
                    result.put(res)
                    logging.info("deploy success")
                    send(BEATS_TOPIC, "deploy success")
                else:
                    res["status"] = "fail"
                    res["result"] = "br-name could found"
                    res["br_name"] = str(cfg_info["br_name"]).encode('utf-8')
                    result.put(res)
                    logging.info("deploy fail")
                    send(BEATS_TOPIC, "deploy fail")
                    continue
            elif j == brlen and match_success is False:
                    logging.info("match br fail")
                    res["status"] = "fail"
                    res["result"] = "br-name could found"
                    res["br_name"] = str(cfg_info["br_name"]).encode('utf-8')
                    result.put(res)
                    logging.info("deploy fail")
                    send(BEATS_TOPIC, "deploy fail")
                    continue
        else:
            sleep(0.5)
            continue


def beats():
    beats_producer = KafkaProducer(bootstrap_servers=KAFKA)
    while True:
        sleep(20)
        beats_producer.send(BEATS_TOPIC, "kafka_deploy_nf alive !")


def sigquit(signo, frame):
    for each in br_list:
        os.system('ovs-vsctl -- clear Bridge %s NetFlow' % each)
    logging.info('catch signal %s , program quit!  NF setting cleared...' % signo)
    log_producer.send(BEATS_TOPIC, "catch signal %s , program quit!  NF setting cleared..." % signo)
    exit(1)
signal.signal(signal.SIGINT, sigquit)

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
    sleep(0.2)
    deploy_producer = KafkaProducer(bootstrap_servers=KAFKA)
    while True:
        d = deploy_result.get()
        if d["status"] == "success":
            br_list.append(d["br_name"].decode('utf-8'))
        deploy_producer.send(topic=DEPLOY_RESULT_TOPIC, value=json.dumps(d).encode('utf-8'))
        logging.info("send a deploy result")
        send(BEATS_TOPIC, "send a deploy result")
