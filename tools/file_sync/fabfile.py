#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/23 14:34
# @Author  : xwh
# @File    : fabfile.py
# from fabric.api import run, env, hosts, roles, task, get, put, cd
from fabric import executor, Connection
import threadpool
import traceback
import os, sys

try:
    import psutil
    thread_num = psutil.cpu_count(True)
except:
    thread_num = 4

# fabric 2
deploy = {
    "group1": ["192.168.3.61", "192.168.3.62","192.168.3.63",
        "192.168.3.64","192.168.3.65","192.168.3.66","192.168.3.67", "192.168.3.68"]
}
# group1 = ["192.168.3.61"]

pwd_dict = {

}

# r = Group(*tuple(group1), ).run("uname")
# g = Group(*tuple(group1), user="root", connect_kwargs={'password': 'asdf1234'})
def th_task(ip):
    c = Connection(ip, user="root", connect_kwargs={'password': '2wsx@WSX1234'})
    try:
        # c.cd("cd /var/log/")
        # c.run("rm -rf /root/xwh/ && mkdir -r /root/xwh/")
        c.put(local="E:/Python Project/*", remote="/root/xwh/")
        r = c.run("pwd")
        print r
    except:
        print traceback.format_exc()

# r = g.put("file_sync.py", "/root/testxwh.py")
# r = g.run("echo hello `uname`")
# for connection, result in r.items():
#     print("{0.host}: {1.stdout}, {1.stderr}".format(connection, result))

if __name__ == '__main__':
    # pool = threadpool.ThreadPool(thread_num)
    # requests = threadpool.makeRequests(th_task, deploy["group1"])
    # [pool.putRequest(req) for req in requests]
    # pool.wait()
    th_task("192.168.3.31")
































# fabric 1
# env.user = "root"
# pass1 = "2wsx@WSX1234"
# pass2 = "asdf1234"
#
#
# # group1 = ["192.168.3.3","192.168.3.4","192.168.3.5", "192.168.3.6", "192.168.3.7", "192.168.3.8",
# #     "192.168.3.42", "192.168.3.44"]
#
# group1 = ["192.168.3.31", "192.168.3.32"]
#
# group2 = ["192.168.3.61", "192.168.3.62","192.168.3.63",
#     "192.168.3.64","192.168.3.65","192.168.3.66","192.168.3.67", "192.168.3.68"]
#
#
# def group_password_gen(group, pwd):
#     return {host: pwd for host in group}
#
#
# env.roledefs = {
#     'compute': group1,
# }
#
# env.passwords.update(group_password_gen(group1, pass1))
#
# @hosts("192.168.3.32")
# def push_file(local_path, remote_path):
#     if local_path[-1] != os.sep: local_path += os.sep
#     if remote_path[-1] != os.sep: remote_path += os.sep
#     with cd(remote_path):
#         run("rm -f /root/xwh/*")
#         put("/root/xwh/*", "/root/xwh/")
#
#
# # @roles("compute")
# # def get_file():
# #     with cd("/root/"):
# #         run("touch 1.txt")
#
# @roles("compute")
# def hello():
#     run("echo 'hello'")
