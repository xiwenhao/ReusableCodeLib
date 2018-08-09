#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: kafka_pro.py
# @time: 2017/8/23 0023 下午 2:17
# @desc:

from time import sleep
from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(bootstrap_servers="192.168.100.15:9092")
msg0 = '{"br_name": "br8", "engine_id": "1", "monitor_ip": "192.168.100.16", "monitor_port": "2055","monitor_status": "1", "target_ip": "192.168.100.223", "target_port": "2055"}'
msg1 = '{"br_name": "br-int", "engine_id": "2", "monitor_ip": "192.168.100.15", "monitor_port": "2055","monitor_status": "1", "target_ip": "192.168.100.223", "target_port": "2055"}'
producer.send("xwh-consumer", msg0)
producer.send("xwh-consumer", msg1)

print msg0
print msg1
