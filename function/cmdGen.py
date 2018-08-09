#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: cmdGen.py
# @time: 2017/11/10 0010 下午 3:26
# @desc:


def _cmdGen(iter_):
    mirror_name_list = iter_["mirror_list"].split(",")
    nic_list = iter_["NIC_list"].split(",")
    cmd = ""
    # 生成 第一行mirror=部分
    mirror_id_list = ["@m%s" % i for i in xrange(0, len(nic_list))]
    cmd += "ovs-vsctl -- set Bridge br-int mirrors="
    for each_id in mirror_id_list:
        cmd += each_id + ","
    cmd = cmd[0:-1] + " "
    # 生成端口 get port 部分
    for name in mirror_name_list:
        for port in iter_[name].split(","):
            cmd += "-- --id=@{port} get Port {port} ".format(port=port)
    # 生成网卡 get port 部分
    for each_nic in nic_list:
        cmd += "-- --id=@{nic} get Port {nic} ".format(nic=each_nic)

    # 生成可选的尾部(select-xxx-port)
    for id, name, nic in zip(mirror_id_list, mirror_name_list, nic_list):
        cmd += "-- --id={id} create Mirror name={name} ".format(id=id, name=name)
        if iter_[name+"_mode"] == "src":
            cmd += "select-src-port="
            for port in iter_[name].split(","):
                cmd += "@%s," % port
            cmd = cmd[0:-1]
        if iter_[name+"_mode"] == "dst":
            cmd += "select-dst-port="
            for port in iter_[name].split(","):
                cmd += "@%s," % port
            cmd = cmd[0:-1]
        if iter_[name+"_mode"] == "all":
            cmd += "select-src-port="
            for port in iter_[name].split(","):
                cmd += "@%s," % port
            cmd = cmd[0:-1] + " "
            cmd += "select-dst-port="
            for port in iter_[name].split(","):
                cmd += "@%s," % port
            cmd = cmd[0:-1]
        cmd += " output-port=@%s " % nic
    cmd += "\n"
    return cmd


if __name__ == '__main__':
    dic = {
        "type": "BGPmirror",
        "time": "1510280908",
        "cmd": "config",
        "mirror_list": "BGPmirror1",
        "NIC_list": "em3",
        "BGPmirror1": "qvo176121c4-84,qvo6d471ef9-71,qvo176121c4-84",
        "BGPmirror1_mode": "dst"
    }
    dic_ = {
        "type": "BGPmirror",
        "time": "1510280908",
        "cmd": "config",
        "mirror_list": "BGPmirror1,FLOWmirror2,BGPmirror2",
        "NIC_list": "em3,em4,em5",
        "BGPmirror1": "port1,port2,port3,port4",
        "FLOWmirror2": "port5,port6,port7,port8",
        "BGPmirror2": "port9,port10",
        "BGPmirror1_mode": "all",
        "BGPmirror2_mode": "src",
        "FLOWmirror2_mode": "all"
    }
print _cmdGen(dic)
# print _cmdGen(dic_)
