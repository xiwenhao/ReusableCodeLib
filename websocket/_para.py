#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: _para.py
# @time: 2018/1/9 0009 上午 11:06
# @author: xwh
# @desc:

import shutil
import hashlib
import paramiko
import json
import os
from paramiko.ssh_exception import SSHException


class Timeout(Exception):
    pass


class HostRefuse(Exception):
    pass


class PasswordError(Exception):
    pass


class SFTP_Base(object):
    def __init__(self, hostIP, username, password, term, width, height, port=22):
        self.trans = paramiko.Transport(sock=(hostIP, port), default_window_size=4097152)
        self.trans.connect(username=username, password=password)
        self.chan = self.trans.open_session()
        self.chan.settimeout(100)
        self.chan.get_pty(term=term, width=int(width), height=int(height))
        self.chan.invoke_shell()

    def close(self):
        self.chan.close()
        self.trans.close()

    def __close__(self):
        self.close()


class Sftp(object):
    upload_dir = "/static/file_op/upload/"
    download_dir = "/static/file_op/download/"

    def __init__(self, hostIP, username, password, token, term, width, height, port=22):
        try:
            print "init SFTP class", hostIP, username, password, token, term, width, height, port
            # sock = (hostIP, port)
            self.trans = paramiko.Transport(sock=(hostIP, int(port)), default_window_size=4097152)
            self.trans.connect(username=username, password=password)
            # print "init para trans ok"
            self.chan = self.trans.open_session()
            self.chan.settimeout(100)
            self.chan.get_pty(term=term, width=int(width), height=int(height))
            self.chan.invoke_shell()
            self.pri_dir = "." + self.upload_dir + token + "/"
            self.dl_dir = "." + self.download_dir + token + "/"
            self.current_part = -1
            self.sftp = paramiko.SFTPClient.from_transport(self.trans)
            self.ssh = paramiko.SSHClient()
            self.ssh._transport = self.trans
            if not os.path.exists(self.pri_dir):
                os.makedirs(self.pri_dir)
                print "create private upload dir:", self.pri_dir
            if not os.path.exists(self.dl_dir):
                os.makedirs(self.dl_dir)
                print "create private dl dir:", self.dl_dir
        except SSHException as e:
            reason = str(e)
            # 所有的错误都在一个异常类里...
            print "%s:%s Connect fail! reason: %s" % (hostIP, port, reason)

            if "Authentication failed" in reason:
                print "password error!"
                raise PasswordError
            if "[Errno 10060]" in reason:
                print "timeout!"
                raise Timeout
            if "[Errno 10061]" in reason:
                print "target host refuse!"
                raise HostRefuse
            raise Exception("connect fail")
        except Exception as e:
            print "unknow sftp error", str(e)
            raise Exception(e)

    def getPrivateDir(self):
        return self.pri_dir

    def sshExec(self, cmd):
        return self.ssh.exec_command(cmd)

    def getMd5(self, abs_filepath):
        _in, _out, _err = self.sshExec("md5sum %s" % abs_filepath.encode("utf-8"))
        return _out.read().encode("utf-8").split(" ")[0]

    def getFileSize(self, abs_filepath):
        _in, _out, _err = self.sshExec("du -b %s" % abs_filepath)
        if _err.readline():
            return "no such file %s" % abs_filepath
        return _out.read().encode("utf-8").split("\t")[0]

    def __del__(self):
        self.close()

    def close(self):
        self.chan.close()
        self.trans.close()
        shutil.rmtree(self.pri_dir)
        shutil.rmtree(self.dl_dir)
        print "del Sftp instance and del temp folder"

    def get_file_md5(self, filepath):
        x = hashlib.md5()
        try:
            f = file(filepath, 'rb')
        except Exception as e:
            err_info = {'ERROR_INFO': str(e)}
            return json.dumps(err_info)

        while True:
            a = f.read(4096)
            if not a:
                break
            x.update(a)

        file_md5 = x.hexdigest()

        return file_md5

    def download_file(self, filename, remote_path):
        local_path = self.dl_dir + filename
        # print "remote path", remotepath
        try:
            self.sftp.get(remote_path, local_path)
            return True
        except Exception:
            return False


    def checkMD5(self, filename, source_file_md5):
        serverpath = self.pri_dir + filename
        server_file_md5 = self.get_file_md5(serverpath)

        if not server_file_md5 == source_file_md5:
            err_info = {'FILE_ERROR': 'File has been damaged'}
            self.sftp.remove(serverpath)
            return json.dumps(err_info)
        else:
            self.sftp.close()
            info = {'STATE': 'File download successful!'}
            return json.dumps(info)

    def upload_file(self, localpath, remotepath):
        try:
            self.sftp.put(remotepath, localpath)
        except Exception as e:
            err_info = {'TRANSMISSION_ERROR': str(e)}
            return json.dumps(err_info)

        # server_file_md5 = self.get_file_md5(localpath)

        # info = {'STATE': 'File upload successful!'}
        # return json.dumps(info), server_file_md5

if __name__ == '__main__':
    trans = paramiko.Transport(sock=("192.168.100.16", 22), default_window_size=4097152)
    trans.connect(username="root", password="bc_13579")
    chan = trans.open_session()
    chan.settimeout(100)
    # chan.get_pty(term=term, width=int(width), height=int(height))
    chan.invoke_shell()
    chan.send("ls\r")
    sftp = paramiko.SFTPClient.from_transport(trans)
    ssh = paramiko.SSHClient()
    ssh._transport = trans
    # sftp.get("/root/CA/.smzh.zip/smzh.zip00000", "./1111.111")
    print chan.recv(65535).decode("utf-8")
