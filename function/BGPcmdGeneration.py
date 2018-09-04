#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: BGPcmdGeneration.py
# @time: 2017/10/17 0017 下午 2:39
# @desc: ovs镜像命令生成(命令行实现)

DEFAULT_NIC = 'em4'

def _cmdGeneration(iter_):
    if len(iter_) != 1:
        cmd = "ovs-vsctl -- set Bridge br-int mirrors=@m "
        for each in iter_:
            cmd += "-- --id=@{port} get Port {port} ".format(port=each)
        cmd += "-- --id=@{NIC} get Port {NIC} -- --id=@m create Mirror name=BGPmirror select-dst-port=".format(
            NIC=DEFAULT_NIC)
        for each in iter_:
            cmd += "@{port},".format(port=each)
        cmd = cmd[0:-1]
        cmd += " select-src-port="
        for each in iter_:
            cmd += "@{port},".format(port=each)
        cmd = cmd[0:-1]
        cmd += " output-port=@{NIC}\n".format(NIC=DEFAULT_NIC)
    else:
        cmd = "ovs-vsctl -- set Bridge br-int mirrors=@m " \
              "-- --id=@{port} get Port {port} " \
              "-- --id=@{NIC} get Port {NIC} -- --id=@m create Mirror name=BGPmirror " \
              "select-dst-port=@{port} " \
              "select-src-port=@{port} output-port=@{NIC}\n".format(port=iter_.pop(), NIC=DEFAULT_NIC)
    return cmd

if __name__ == '__main__':
    s = raw_input()
    port_list= s.split(",")
    print _cmdGeneration(port_list)