#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: set_nic_ip.py
# @time: 2017/12/8 0008 下午 1:27
# @author: xwh
# @desc:
import os


def setNicIpAndPutInNetns(ip, nic_name, ns_name, mask):
    try:
        os.system("ip link set {nic_name} netns {ns_name}".format(nic_name=nic_name, ns_name=ns_name))
        os.system("ip netns exec {ns_name} ip addr add {ip}/{mask} dev {nic_name}".format(
            ns_name=ns_name, ip=ip, mask=mask, nic_name=nic_name))
        os.system("ip netns exec {ns_name} ip link set {nic_name} up".format(ns_name=ns_name, nic_name=nic_name))
    except Exception as e:
        raise e
