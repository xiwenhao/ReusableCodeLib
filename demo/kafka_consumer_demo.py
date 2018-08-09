#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_consumer_demo.py
# @time: 2017/9/29 0029 下午 3:34
# @desc:
from kafka import KafkaConsumer


KAFKA = "192.168.6.22:9092"
CONFIG_TOPIC = "STATUS_OVS"

consumer = KafkaConsumer(CONFIG_TOPIC, bootstrap_servers=KAFKA)

for i in consumer:
    print i.value