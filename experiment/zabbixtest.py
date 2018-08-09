#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: zabbixtest.py
# @time: 2017/12/22 0022 下午 2:27
# @author: xwh
# @desc:
from pyzabbix import ZabbixAPI

zab = ZabbixAPI("http://192.168.100.101/zabbix")
zab.login("Admin", "zabbix")

# for i in zab.application.get(output="extend"):
#     print i["name"], i["applicationid"], i["hostid"]
for i in zab.item.get(output="extend", search={}):
    print i
