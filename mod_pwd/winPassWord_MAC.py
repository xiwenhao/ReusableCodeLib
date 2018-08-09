#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: modify_pwd.py
# @time: 2018/3/5 0005 上午 10:01
# @author: xwh
# @desc:

from hashlib import md5 as MD5
from os import system, remove
from netifaces import interfaces, ifaddresses
from getpass import getuser
# base_url = "http://169.254.169.254/openstack/latest/meta_data.json"
# r = get(base_url)
# meta_json = loads(r.content)
# print "request metadata json status code", r.status_code
s = set()
sum = 0
for i in interfaces():
    s.add(ifaddresses(i)[-1000][0]["addr"])
for i in s:
    l = i.split(":")
    if len(l) == 1: continue
    # l = list()
    if l.count("00") > 5: continue
    for n in l:
        sum += int(n, 16)
md5pwd = MD5(str(sum)).hexdigest()
# print sum, md5pwd
pwd = md5pwd if len(md5pwd) <= 10 else md5pwd[0:10]
username = getuser()
# # logoff注销
system("net user %s %s" % (username, pwd))
# print username, pwd
# print "init password done! currrent user is [%s]" % username, "new password is [%s]" % pwd
# raw_input("push enter to quit!")
#
# remove(argv[0])
