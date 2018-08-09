#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: add_ovs_nic.py
# @time: 2017/12/8 0008 下午 1:27
# @author: xwh
# @desc:
from subprocess import Popen, PIPE
import os


def addOvsNicAndSetTag(nic_name, br_name, tag):
    handler = Popen("ovs-vsctl add-port {br_name} {nic_name} -- set interface {nic_name} type=internal".format(
        br_name=br_name, nic_name=nic_name), shell=True, stderr=PIPE, stdout=PIPE)
    if handler.stderr.readline() != 0:
        handler.kill()
        return False
    else:
        os.system("ovs-vsctl set port {nic_name} tag={tag}".format(nic_name=nic_name, tag=tag))
        handler.kill()
        return True
