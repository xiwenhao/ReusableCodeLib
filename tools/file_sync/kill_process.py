#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/25 9:56
# @Author  : xwh
# @File    : kill_process.py

import psutil
import sys
import os

def mutex_process(python_process_name):
    for process in psutil.process_iter():
        p = psutil.Process(process.pid)
        cmdline = p.cmdline()[:3]
        self_pid = os.getpid()
        # if len(cmdline) and "python" in cmdline[0]: print p.name(), cmdline
        if p.pid != self_pid and len(cmdline) > 1 and "python" in cmdline[0] and python_process_name in cmdline[1]:
            os.kill(p.pid, 9)

if __name__ == '__main__':
    mutex_process(sys.argv[1])