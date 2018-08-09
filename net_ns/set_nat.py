#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: set_nat.py
# @time: 2017/12/8 0008 下午 1:28
# @author: xwh
# @desc:            left(内网段虚拟机)                                      right(外网段服务器)
#        ___________    __________________________________________________     _____________
#        |   VM    |    |                                                |     |  SERVER   |
#        |    vm_ip|----|                 OVS-TRUNK                      |-----|server_ip  |
#        |   vm_tag|    |                                                |     |server_tag |
#        -----------    --------------------------------------------------     -------------
#                                 |                        |
#                                 |                        |
#                                 |                        |
#                       ----------------------------------------------------
#                       |       vmethl                vmethr               |
#                       |       vmethl_ip             vmethr_ip            |
#                       |       vmethl_tag=vm_tag     vmethr_tag=server_tag|
#                       |                                                  |
#                       |                   NET NS                         |
#                       ----------------------------------------------------
#
#                            左侧通向内网段                右侧通向外网段
# server proxy: vm -> vmethl ->(nat)-> vmethr -> server
import os


def setServerProxyNat(ns_name, vethl_ip, vethr_ip, server_ip, port2vm, server_port):
    '''
    :param ns_name: netns
    :param vethl_ip: netns中虚拟机侧网卡的地址(也是对虚拟机暴露地址)
    :param vethr_ip: netns中服务器侧网卡的地址
    :param server_ip: 真正提供服务的服务器地址
    :param port2vm: 对虚拟机暴露的端口
    :param server_port: 真正提供服务的服务器端口
    :return: None
    '''
    os.system("ip netns exec {ns_name} echo 1 > /proc/sys/net/ipv4/ip_forward".format(ns_name=ns_name))
    os.system("ip netns exec {ns_name} iptables -t nat -A PREROUTING -d {vethl_ip} -p tcp --dport {port2vm} \
                -j DNAT --to-destination {server_ip}:{server_port}".format(
        ns_name=ns_name, vethl_ip=vethl_ip, port2vm=port2vm, server_ip=server_ip, server_port=server_port))
    os.system("ip netns exec {ns_name} iptables -t nat -A POSTROUTING -d {server_ip} -p tcp --dport {server_port} \
                -j SNAT --to {vethr_ip}".format(
        ns_name=ns_name, server_ip=server_ip, server_port=server_port, vethr_ip=vethr_ip))


def setSshProxyNat(ns_name, vethl_ip, vethr_ip, vm_ip, port2visiter, vm_port):
    '''
    :param ns_name: netns
    :param vethl_ip: netns中虚拟机侧的网卡的ip
    :param vethr_ip: netns中外网侧的网卡的ip
    :param vm_ip: 需要被ssh的虚拟机ip
    :param port2visiter: 在外网中暴露的端口
    :param vm_port: 虚拟机的端口如22
    :return: None
    '''
    os.system("ip netns exec {ns_name} echo 1 > /proc/sys/net/ipv4/ip_forward".format(ns_name=ns_name))
    os.system("ip netns exec {ns_name} iptables -t nat -A PREROUTING -d {vethr_ip} -p tcp \
                --dport {port2visiter} -j DNAT --to {vm_ip}:{vm_port}".format(
        ns_name=ns_name, vethr_ip=vethr_ip, port2visiter=port2visiter, vm_ip=vm_ip, vm_port=vm_port))
    os.system("ip netns exec {ns_name} iptables -t nat -A POSTROUTING -d {vm_ip} -p tcp \
                --dport {vm_port} -j SNAT --to {vethl_ip}".format(
        ns_name=ns_name, vm_ip=vm_ip, vm_port=vm_port, vethl_ip=vethl_ip))














