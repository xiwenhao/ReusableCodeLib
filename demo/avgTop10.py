#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/22 16:30
# @Author  : xwh
# @File    : avgTop10.py

import json
from subprocess import Popen, PIPE
from time import time

import psutil

try:
    import cPickle as pickle
except ImportError:
    import pickle

AvgTopFile = "./.AvgTopFile.tmp"


# if not (os.path.exists("./static/file_op/upload") and os.path.exists("./static/file_op/download")):
#     os.makedirs("%s/web/static/file_op/" % os.path.abspath(os.curdir))
#     print "mkdir static/file_op"
#     os.system("mount -t tmpfs -o size=1G tmpfs %s/web/static/file_op/" % os.path.abspath(os.curdir))
#     print "mount tmpfs"
# if not os.path.exists("./static/file_op/upload"):
#     os.makedirs("./static/file_op/upload")
# if not os.path.exists("./static/file_op/download"):
#     os.makedirs("./static/file_op/download")


h = Popen("ps -aux", shell=True, stdout=PIPE)
_out = h.stdout.readlines()
pro_info = []
data = {}
_out.pop(0)
for eachline in _out:
    out = [i for i in eachline.split(" ") if len(i)]
    pro_info.append((out[1], float(out[2]), float(out[3])))
#         user    pid  %cpu   %mem
# out = ['root','5492','0.0','0.0','0','0','?','S<','6\xe6\x9c\x8806','0:10','[kworker/15:1H]\n']

for pid, cpu, mem in pro_info:
    try:
        p = psutil.Process(int(pid))
    except psutil.NoSuchProcess:
        continue
    pname = p.name()
    # if pname+"@"+pid in data:
    # data.update({
    #     "process_name@pid": {
    #         "last_n_cpu": [],
    #         "last_n_mem": [],
    #         "current_avg_cpu": "",
    #         "current_avg_mem": "",
    #         "last_update": time()
    #     }
    # })
    data.update({
        pname + "@" + str(pid): {
            "cpu": cpu,
            "mem": mem
        }
    })
    # else
with open(AvgTopFile, "r") as f:
    file_data = json.loads(f.read())
    print file_data
    print len(file_data)

for k,v in data.items():
    if k in file_data:
        if file_data[k]["last_update"] <= (time() - 60):
            del file_data[k]
            continue
        if len(file_data[k]["last_n_cpu"]) == 20: file_data[k]["last_n_cpu"].pop(0)
        if len(file_data[k]["last_n_mem"]) == 20: file_data[k]["last_n_mem"].pop(0)
        file_data[k]["last_n_cpu"].append(v["cpu"])
        file_data[k]["last_n_mem"].append(v["mem"])
        file_data[k]["current_avg_cpu"] = float(sum(file_data[k]["last_n_cpu"])) / len(file_data[k]["last_n_cpu"])
        file_data[k]["current_avg_mem"] = float(sum(file_data[k]["last_n_mem"])) / len(file_data[k]["last_n_mem"])
        file_data[k]["last_update"] = time()
    else:
        file_data.update({
            k: {
                "last_n_cpu": [v["cpu"],],
                "last_n_mem": [v["mem"],],
                "current_avg_cpu": float(v["cpu"]),
                "current_avg_mem": float(v["mem"]),
                "last_update": 0
            }
        })
with open(AvgTopFile, "w+") as f:
    f.write(json.dumps(file_data))

# with open(AvgTopFile, "r") as f:
#     file_data = json.loads(f.read())
#     print json.dumps(file_data)