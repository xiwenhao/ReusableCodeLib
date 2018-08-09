#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/2 14:08
# @Author  : xwh
# @File    : FTPdownloader.py

from ftplib import FTP, error_perm
import os

# 起始ftp路径
start_path = "/PIPLIBS/"
# 保存在当前目录下download文件夹下
local_dir = "download"


ftp = FTP()

ftp.connect("192.168.100.18", port=21)
# ftp 账号密码
ftp.login(user="", passwd="")

# 待下载目录
dir_list = {start_path,}

def downloadFromIter():
    if not dir_list:
        print "all download complete"
        return
    else:
        ftp.cwd(dir_list.pop())
    for filename in ftp.nlst():
        try:
            if not os.path.isdir("./" + local_dir + ftp.pwd() + "/"):
                os.makedirs("./" + local_dir + ftp.pwd() + "/")
            # if os.path.exists("./" + local_dir + ftp.pwd() + "/" + filename):
            #     continue
            with open("./" + local_dir + ftp.pwd() + "/" + filename, "wb") as fp:
                print "download file:", filename, "localpath:", "./" + local_dir + ftp.pwd() + "/" + filename
                ftp.retrbinary("RETR " + filename, fp.write, 4096)
                print "download done", ftp.pwd() + "/" + filename
        except error_perm:
            print filename, "is not file mkdir", "./" + local_dir + ftp.pwd() + "/"
            os.remove("./" + local_dir + ftp.pwd() + "/" + filename)
            dir_list.add(ftp.pwd() + "/" + filename)
            if not os.path.isdir("./" + local_dir + ftp.pwd() + "/" + filename):
                os.makedirs("./" + local_dir + ftp.pwd() + "/" + filename)
    downloadFromIter()
downloadFromIter()

