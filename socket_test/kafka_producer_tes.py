#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_producer_tes.py
# @time: 2017/11/13 0013 上午 10:28
# @desc:

from kafka import KafkaProducer
import time
pro = KafkaProducer(bootstrap_servers="192.168.100.15:9092", acks=0)

while True:
    pro.send("xwh-test", str(time.time()))