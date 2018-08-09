#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: functe.py
# @time: 2017/11/15 0015 下午 2:22
# @author: xwh
# @desc:
import multiprocessing as mp
import time

def p1(dict, lock):
    print "p1start"
    i = 0
    while True:
        try:
            i += 1
            lock.acquire()
            print "p1 end"
            print dict
            dict.clear()
            time.sleep(0.1)
            print "p1 clear"

            lock.release()
        except KeyError:
            continue



def p2(dict, lock):
    print "p2start"
    i = 0
    while True:
        try:
            lock.acquire()
            print "p2 get lock"
            print "p2 write"
            dict["src"] = "src_mac_etc"
            lock.release()
        except KeyError:
            continue


if __name__ == '__main__':
    mng = mp.Manager()
    lock = mng.Lock()
    dic = mng.dict()
    pr1 = mp.Process(target=p1, args=(dic,lock))
    pr2 = mp.Process(target=p2, args=(dic,lock))
    pr1.start()
    pr2.start()
    pr1.join()
    pr2.join()
