#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: trans_ns.py
# @time: 2017/10/26 0026 上午 10:10
#  argv1 ovs-br
# ip in subnet 应该是与内部虚拟机网段相同 ip to ftp应该与ftp同网段

import socket
import os
import sys

# ns_name = ($IP)_($br-name)_trans_netns
hostIP = socket.gethostbyname(socket.gethostname())
DEFAULT_NIC = "em1"

# 四个ip
ip_in_subnet = ""
ip_to_ftp = ""
ip_in_subnet_peer = ""
ip_to_ftp_peer = ""


br_list = sys.argv[1].split(",")
for br_name in br_list:
    ns_name = hostIP + br_name + "_trans_netns"
    # 删除重复
    os.system("ip netns del {ns_name} &>/dev/null".format(ns_name=ns_name))
    # 建立netns
    os.system("ip netns add {ns_name}".format(ns_name=br_name))
    # 创建对等体veth和vpeer, 1为子网内 2为子网外
    veth1 = br_name + "_veth1"
    veth2 = br_name + "_veth2"
    vpeer1 = br_name + "_vpeer1"
    vpeer2 = br_name + "_vpeer2"

    os.system("ip link add {veth1} type veth peer name {vpeer1}".format(veth1=veth1, vpeer1=vpeer1))
    os.system("ip link add {veth2} type veth peer name {vpeer2}".format(veth2=veth2, vpeer2=vpeer2))
    # 添加到netns
    os.system("ip link set {vpeer1} netns {ns_name}".format(vpeer1=vpeer1, ns_name=ns_name))
    os.system("ip link set {vpeer2} netns {ns_name}".format(vpeer2=vpeer2, ns_name=ns_name))
    # 设定veth的ip并启动
    os.system("ip addr add {veth_ip1}/24 dev {veth1}".format(veth_ip1=ip_in_subnet, veth1=veth1))
    os.system("ip addr add {veth_ip2}/24 dev {veth2}".format(veth_ip2=ip_to_ftp, veth2=veth1))
    os.system("ip link set {veth1} up".format(veth1=veth1))
    os.system("ip link set {veth2} up".format(veth2=veth2))

    # 设置ns内对等体vpeer的ip 并启用
    os.system("ip netns exec {ns_name} ip addr add {vpeer_ip1}/24 dev {vpeer1}".format(
        ns_name=ns_name, vpeer_ip1=ip_in_subnet_peer, vpeer1=vpeer1))
    os.system("ip netns exec {ns_name} ip addr add {vpeer_ip2}/24 dev {vpeer2}".format(
        ns_name=ns_name, vpeer_ip2=ip_to_ftp_peer, vpeer2=vpeer2))

    os.system("ip netns exec {ns_name} ip link set {vpeer1} up".format(ns_name=ns_name, vpeer1=vpeer1))
    os.system("ip netns exec {ns_name} ip link set {vpeer2} up".format(ns_name=ns_name, vpeer2=vpeer2))

    # 离开netns的流量通过veth2  ip netns exec {ns_name} iptables -t nat -A PREROUTING -i {vpeer1} -j DNAT -to {to_ftp_ip_port}
    os.system("ip netns exec {ns_name} ip route add default via {eth2_ip_to_ftp}".format(
        ns_name=ns_name, eth2_ip_to_ftp=ip_to_ftp))

    # 添加veth到ovs网桥
    os.system("ovs-vsctl add port {br_name} {veth1}".format(br_name=br_name, veth1=veth1))
    os.system("ovs-vsctl add port {br_name} {veth2}".format(br_name=br_name, veth2=veth2))

    # FIXME 配置ns内部iptables转发
    os.system("ip netns exec {ns_name} iptables -A FORWARD -i {vpeer1} -o {vpeer2} -j ACCEPT".format(
        ns_name=ns_name, vpeer1=vpeer1, vpeer2=vpeer2))
    os.system("ip netns exec {ns_name} iptables -A FORWARD -o {vpeer1} -i {vpeer2} -j ACCEPT".format(
        ns_name=ns_name, vpeer1=vpeer1, vpeer2=vpeer2))
    # TODO 宿主机端口转发nat 或者镜像
    os.system("")
    os.system("")
    os.system("")
