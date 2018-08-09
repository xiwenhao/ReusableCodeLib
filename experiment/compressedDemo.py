#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: yasuowenjian.py
# @time: 2018/1/18 0018 上午 11:03
# @author: xwh
# @desc:

import zipfile

# z = zipfile.ZipFile("D:\\zipfile\\sflowtool.zip", "r")
# # print z.namelist()
# z.extractall(path="D:\\zipfile\\sflowtool.zip")
# print "unzip ok"
# with open('D:\\zipfile\\sflowtool.zip', 'rb') as MyZip:
#   print(MyZip.read(4))
z = zipfile.ZipFile("D:\\zipfile\\sflowtool.zip", "r")
for name in z.namelist():
    z.extract(name)
print "extra OK"