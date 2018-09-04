#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/23 21:30
# @Author  : xwh
# @File    : qga_connect_tes.py
import requests
from settings import ip_list
# from threading import Timer
# ip_list = ["192.168.3.31:9000"]
fail_list = []
for ip in ip_list:
    try:
        r = requests.get(url="http://"+ip+":9000", timeout=1)
        print ip, r.status_code, r.content
        if r.status_code != requests.codes.ok: fail_list.append(ip)
    except requests.Timeout:
        fail_list.append(ip)
        print ip,  "timeout "
print "ip list", ip_list
print "fail list", fail_list