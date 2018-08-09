#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_comsumer_tes.py
# @time: 2017/11/13 0013 上午 10:31
# @desc:

from kafka import KafkaConsumer

consumer = KafkaConsumer("xwh-test", bootstrap_servers="192.168.100.15:9092")
while True:
    msg = next(consumer)
    print msg.value