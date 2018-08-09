#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: unit_t.py
# @time: 2017/11/13 0013 下午 2:21
# @desc:

SUPPORT_FUNC = ['config','stop','delete','query']
def checkKeyInDict(iter_):
    '''
    "type":"BGPmirror",
    "time":"1510280908",
    "cmd":"config",
    "mirror_list":"BGPmirror1,FLOWmirror2",
    "NIC_list":"em3,em4",
    "BGPmirror1":"port1,port2,port3,port4",
    "FLOWmirror2":"port5,port6,port7,port8",
    "BGPmirror1_mode":"dst",
    "FLOWmirror2_mode":"all"
    '''

    try:
        if iter_["cmd"] == "config":
            for mirror_name in iter_["mirror_list"].split(","):
                if mirror_name not in iter_.keys():
                    return False
                if mirror_name + "_mode" not in iter_.keys():
                    return False
        if iter_["cmd"] not in SUPPORT_FUNC:
            return False
        else:
            return True
    except KeyError:
        return False


if __name__ == '__main__':
    dic = {
    "type":"BGPmirror",
    "time":"1510280908",
    "cmd":"config",
    "mirror_list":"BGPmirror1,FLOWmirror2",
    "NIC_list":"em3,em4",
    "BGPmirror1":"port1,port2,port3,port4",
    "FLOWmirror2":"port5,port6,port7,port8",
    "BGPmirror1_mode":"dst",
    "FLOWmirror2_mode":"all"
    }
    print checkKeyInDict(dic)