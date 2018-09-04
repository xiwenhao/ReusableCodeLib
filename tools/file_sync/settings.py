#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 9:38
# @Author  : xwh
# @File    : settings.py
from file_sync import *

# server addr
ip_list = [
    "192.168.3.3","192.168.3.4","192.168.3.5", "192.168.3.6", "192.168.3.7", "192.168.3.8",
    "192.168.3.42", "192.168.3.44", "192.168.3.48",
    "192.168.3.61", "192.168.3.62","192.168.3.63","192.168.3.64","192.168.3.65",
    "192.168.3.66","192.168.3.67", "192.168.3.68",
    "192.168.3.69", "192.168.3.70", "192.168.3.71", "192.168.3.72"
           # "192.168.3.31"
           ]
# ip_list = []
# ip_list = ["192.168.3.3"]

# server password
pwd_list = [ "asdf1234", "2wsx@WSX1234",]

# sync_file = True
sync_file = False

remote_path = "/root/xwh/KVMstatus"
local_path = "E:\\Python Project\\KVMstatus" # 此目录下的每一个文件夹都会在remote_path下建立同名目录
# "E:\\Python Project\\file_sync" --> "/root/xwh/file_sync"

# start_cmd_list = [
start_cmd_list = [
    # "rm -rf /root/xwh",
    # "mkdir -p /root/xwh"
    # "nohup python /root/xwh/file_io_service/kill_process.py vMonitorKafka_v0.1.py > /dev/null 2>&1 &",
    # "nohup python /root/xwh/file_io_service/kill_process.py file_io_app.py > /dev/null 2>&1 &",

]
# cmd_list = []
# cmd_list = ["iptables -A INPUT -p tcp --dport 9000 -j ACCEPT;iptables -A OUTPUT -p tcp --sport 9000 -j ACCEPT"]
# cmd_list = ["cd /root/xwh/file_io_service; nohup python file_io_app.py &;sleep 0.5"]
end_cmd_list = [
    # "ps -aux ",
    # "iptables -A INPUT -p tcp --dport 9000 -j ACCEPT;iptables -A OUTPUT -p tcp --sport 9000 -j ACCEPT",

    # "cd /root/xwh/TrafficFlow/ && (nohup python set_ovs_sflow.py > nohup.out 2>&1 &)",
    # "cd /root/xwh/TrafficFlow/ && (nohup python traffic_sflow.py > nohup.out 2>&1 &)",

    # "cd /root/xwh/file_io_service && (nohup python file_io_app.py > nohup.out 2>&1 &)",
    # "cd /root/xwh/KVMstatus/ && (nohup python vMonitorKafka_v0.1.py > nohup.out 2>&1 &)",
    # "ovs-appctl -t ovsdb-server ovsdb-server/add-remote ptcp:6640 && sleep 1",
    # "ovs-vsctl set-manager tcp:127.0.0.1:6640 && sleep 1"
    # "cd /root/xwh/TrafficFlow/ && (nohup python vMonitorKafka_v0.1.py > nohup.out 2>&1 &)",
    # "nohup python /root/xwh/file_io_service/file_io_app.py > /dev/null 2>&1 &",
    # "nohup python /root/xwh/KVMstatus/vMonitorKafka_v0.1.py > /dev/null 2>&1 &",
    # "chmod 777 /root/xwh/TrafficFlow/install_sflow_tool.sh",
    # "nohup /root/xwh/TrafficFlow/install_sflow_tool.sh > /dev/null 2>&1 &",
    # "nohup ovs-appctl -t ovsdb-server ovsdb-server/add-remote ptcp:6640 > /dev/null 2>&1 &",
    # "nohup ovs-vsctl set-manager tcp:127.0.0.1:6640 > /dev/null 2>&1 &",
    # "nohup python /root/xwh/TrafficFlow/traffic_sflow.py > /dev/null 2>&1 &"
    # "iptables -A INPUT -p tcp --dport 9000 -j ACCEP",
    # "iptables -A OUTPUT -p tcp --sport 9000 -j ACCEPT",
    # "yum install -y python-pip"
    # "pip install apscheduler kafka flask gevent",
    # "nohup python /root/xwh/file_io_service/file_io_app.py > /dev/null 2>&1 &",
]
# 文件已上传到/root/xwh/

if __name__ == '__main__':
    just_do_it(ip_list)