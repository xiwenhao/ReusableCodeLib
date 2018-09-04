#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/22 9:34
# @Author  : xwh
# @File    : file_sync.py

from settings import *
import datetime
import os, time
import threadpool
import traceback
from paramiko.ssh_exception import SSHException
import paramiko
from fabric import executor, Connection

try:
    import psutil
    thread_num = psutil.cpu_count(True)
except:
    thread_num = 4

online_host = []
fail_host = []
success_host = []

def upload(local_dir, remote_dir, paramiko_obj):
    try:
        t = paramiko_obj.trans
        sftp = paramiko_obj.sftp
        print('upload file start %s %s' % (datetime.datetime.now(), paramiko_obj.host_ip))
        for root, dirs, files in os.walk(local_dir):
            # print('[%s][%s][%s]' % (root, dirs, files))
            for filespath in files:
                local_file = os.path.join(root, filespath)
                a = local_file.replace(local_dir, '').replace('\\', '/').lstrip('/')
                remote_file = os.path.join(remote_dir, a).replace('\\', '/')
                try:
                    sftp.put(local_file, remote_file)
                except Exception as e:
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file, remote_file)
            for name in dirs:
                local_path = os.path.join(root, name)
                a = local_path.replace(local_dir, '').replace('\\', '/').lstrip('/')
                remote_path = remote_dir + a
                # print(33, remote_path)
                try:
                    sftp.mkdir(remote_path)
                    # print(44, "mkdir path %s" % remote_path)
                except Exception as e:
                    # print("mkdir "+ str(e)+ ",dir exist")
                    pass
        print('upload file all success %s ' % datetime.datetime.now())
        # t.close()
    except Exception as e:
        print(88, e)


class FileSync(object):
    def __init__(self, hostIP, pwd):
        self.host_ip = hostIP
        self.pwd = pwd
        self.trans = paramiko.Transport(sock=(hostIP, 22), default_window_size=4097152)
        self.trans.connect(username="root", password=pwd)
        self.chan = self.trans.open_session()
        self.chan.settimeout(100)
        self.chan.get_pty(term="xterm", width=1000, height=10000)
        self.chan.invoke_shell()
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.trans
        self.c = Connection(self.host_ip, user="root", connect_kwargs={'password': self.pwd})
        self.sync_remote_path = remote_path
        self.local_path = local_path

    def sshExec(self, cmd):
        try:
            return self.c.run(cmd)
        except Exception:
            return traceback.format_exc()

def th_task(hostIP):
    try_time = 0
    # 尝试密码列表
    for pwd in pwd_list:
        try:
            para = FileSync(hostIP, pwd)
            break
        except SSHException:
            try_time += 1
            continue
        if try_time == len(pwd_list):
            # 最大尝试次数等于密码列表长度
            print hostIP, "pwd error exit, retry time:", try_time
            fail_host.append(hostIP)
            return
    if start_cmd_list:
        # 先执行的命令
        for cmd in start_cmd_list:
            res = para.sshExec(cmd)
            print "-------\n",hostIP, "exec start cmd [%s] res=[%s]" % (cmd, res), "\n-------\n", #"\n return stdout:[%s] stderr:[%s]\n" % (str(stdout.readlines()), str(stderr.readlines()))
            time.sleep(0.05)
    if sync_file:
        # 上传文件打开
        upload(local_dir=local_path,remote_dir=remote_path, paramiko_obj=para)
        print hostIP, "sync done"
    if end_cmd_list:
        # 上传完文件执行的命令
        for cmd in end_cmd_list:
            res = para.sshExec(cmd)
            print "-----\n",hostIP, "exec end cmd [%s] res=[%s]" % (cmd, res), "\n-------\n", #"\n return stdout:[%s] stderr:[%s]\n" % (str(stdout.readlines()), str(stderr.readlines()))
            time.sleep(0.05)
    success_host.append(hostIP)
    print hostIP, "quit, task done "

def just_do_it(ip_list):
    if not os.path.isdir(local_path):
        print "local path not exist"
        exit(-1)
    pool = threadpool.ThreadPool(thread_num)
    requests = threadpool.makeRequests(th_task, ip_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    print set(ip_list) - set(success_host)
    print "sync all done, fail host:", fail_host, "success_host:", success_host

if __name__ == '__main__':
    just_do_it(ip_list)