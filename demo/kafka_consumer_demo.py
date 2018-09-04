#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_consumer_demo.py
# @time: 2017/9/29 0029 下午 3:34
# @desc:
from kafka import KafkaConsumer


KAFKA = "192.168.3.32:9092"
CONFIG_TOPIC = "OPERATION"

consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)

for i in consumer:
    v = str(i.value)
    if "heartbeat" not in v:
        print v
