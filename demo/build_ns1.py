#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: build_ns1.py
# @time: 2017/12/4 0004 上午 9:50
# @author: xwh
# @desc:
import os


os.system("ip netns del ns1 &>/dev/null ")
os.system("ip netns add ns1 ")
os.system("ip link add vmeth1 type veth peer name vmpeer1 ")
os.system("ip link set vmpeer1 netns ns1 ")
os.system("ip addr add 192.168.101.101/24 dev vmeth1 ")
os.system("ip link set vmeth1 up ")
os.system("ip netns exec ns1 ip addr add 192.168.101.102/24 dev vmpeer1 ")
os.system("ip netns exec ns1 ip link set vmpeer1 up ")
os.system("ip netns exec ns1 ip link set lo up ")
os.system("ip netns exec ns1 ip route add default via 192.168.101.101 ")
os.system("echo 1 > /proc/sys/net/ipv4/ip_forward ")
os.system("iptables -P FORWARD DROP ")
os.system("iptables -F FORWARD ")
os.system("iptables -t nat -F ")
# os.system(" ")
# os.system(" ")
# os.system(" ")
# os.system(" ")
# os.system(" ")



