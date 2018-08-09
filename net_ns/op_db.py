#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: op_db.py
# @time: 2017/12/8 0008 下午 2:29
# @author: xwh
# @desc: sqlite 表名 netns 字段: id(key) datetime status(y/n) ns_type(server/ssh) ns_name ns2vm_nic_name ns2vm_tag ns2vm_ip
# ns2server_nicc_name ns2server_tag ns2server_ip port2vm server_ip server_port

import sqlite3
import time

conn = sqlite3.connect("d:\\net_ns.db")


def queryDB(conn):
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM test_table")
    for row in res:
        yield {
            "id": row[0],
            "datetime": row[1].encode("utf-8"),
            "stamp": time.mktime(time.strptime(row[1].encode("utf-8"), "%Y-%m-%d %H:%M:%S")),
            "status": row[2].encode("utf-8"),
            "ns_type": row[3].encode("utf-8"),
            "ns_name": row[4].encode("utf-8"),
            "ns2vm_nic_name": row[5].encode("utf-8"),
            "ns2vm_tag": row[6],
            "ns2vm_ip": row[7].encode("utf-8"),
            "ns2server_nic_name": row[8].encode("utf-8"),
            "ns2server_tag": row[9],
            "ns2server_ip": row[10].encode("utf-8"),
            "port2vm": row[11],
            "server_ip": row[12].encode("utf-8"),
            "server_port": row[13]
        }


def insertDB(conn, data_dict):
    cur = conn.cursor()



















