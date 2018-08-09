#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: sflow_filter_producer_demo.py
# @time: 2017/9/15 0015 上午 11:11
# @desc:
from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(bootstrap_servers="192.168.100.15:9092")
CONFIG_TOPIC = "SFLOW_FILTER_CONFIG"

msg0 = '{"operation":"sub","agent":"192.168.100.13","key":"fa:16:3e:83:fd:96"}'
producer.send(CONFIG_TOPIC, msg0)
producer.flush()
print msg0
