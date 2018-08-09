#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: aboutIni.py
# @time: 2017/12/15 0015 下午 1:42
# @author: xwh
# @desc:

import ConfigParser


hostIP = "192.168.100.13"
iniFilePath = "./conf.ini"
conf = ConfigParser.ConfigParser()

conf.add_section("sflow_cfg")
conf.set("sflow_cfg", "KAFKA", "192.168.100.16:9092,192.168.100.17:9092,192.168.100.18:9092")
conf.set("sflow_cfg", "PRODUCER_TOPIC", "STATUS_OVS")
conf.set("sflow_cfg", "CONFIG_TOPIC", "_SFLOW_FILTER_CONFIG")
conf.set("sflow_cfg", "LOG_TOPIC", "OPERATION")
conf.set("sflow_cfg", "SFLOW_PORT", "6343")
conf.set("sflow_cfg", "REPORT_INTERVAL", "5")
# KAFKA = "192.168.100.15:9092"
# DEFAULT_BR = "br-int"
# CONFIG_TOPIC = hostIP + "_BGP_MIRROR_CONFIG"
# LOG_TOPIC = "BGP_MIRROR_OPERATION"

conf.add_section("mirror_cfg")
conf.set("mirror_cfg", "KAFKA", "192.168.100.16:9092,192.168.100.17:9092,192.168.100.18:9092")
conf.set("mirror_cfg", "DEFAULT_BR", "br-int")
conf.set("mirror_cfg", "CONFIG_TOPIC", "_BGP_MIRROR_CONFIG")
conf.set("mirror_cfg", "LOG_TOPIC", "BGP_MIRROR_OPERATION")

# 信息写入ini文件
# with open(iniFilePath, "w+") as fp:
#     conf.write(fp)

# sflow 读取必须只读属性否则覆盖源文件变为空
with open(iniFilePath, "r") as fp:
    conf.readfp(fp)
    KAFKA = conf.get("sflow_cfg", "KAFKA").split(",")
    PRODUCER_TOPIC = conf.get("sflow_cfg", "PRODUCER_TOPIC")
    CONFIG_TOPIC = hostIP + conf.get("sflow_cfg", "CONFIG_TOPIC")
    LOG_TOPIC = conf.get("sflow_cfg", "LOG_TOPIC")
    SFLOW_PORT = conf.get("sflow_cfg", "SFLOW_PORT")
    REPORT_INTERVAL = int(conf.get("sflow_cfg", "REPORT_INTERVAL"))

    print KAFKA, PRODUCER_TOPIC, CONFIG_TOPIC, LOG_TOPIC, SFLOW_PORT, REPORT_INTERVAL
# mirror
with open(iniFilePath, "r") as fp:
    KAFKA = conf.get("mirror_cfg", "KAFKA").split(",")
    DEFAULT_BR = conf.get("mirror_cfg", "DEFAULT_BR")
    CONFIG_TOPIC = hostIP + conf.get("mirror_cfg", "CONFIG_TOPIC")
    LOG_TOPIC = conf.get("mirror_cfg", "LOG_TOPIC")
    print KAFKA, DEFAULT_BR, CONFIG_TOPIC, LOG_TOPIC
