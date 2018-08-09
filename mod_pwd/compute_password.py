#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/14 9:11
# @Author  : xwh
# @File    : compute_password.py
from hashlib import md5 as MD5

mac_list = ["a4:34:d9:c5:04:c1", "00:0c:29:d3:22:2f"]
sum = 0
for i in mac_list:
    l = i.split(":")
    if len(l) == 1: continue
    # l = list()
    if l.count("00") > 5: continue
    for n in l:
        sum += int(n, 16)
md5pwd = MD5(str(sum)).hexdigest()
# print sum, md5pwd
pwd = md5pwd if len(md5pwd) <= 10 else md5pwd[0:10]

print "pwd:", pwd