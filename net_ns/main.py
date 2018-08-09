#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: main.py
# @time: 2017/12/8 0008 下午 5:15
# @author: xwh
# @desc:
# 线程0 从kafka接收信息 存入数据库 任务发送到任务队列 task_q
# 线程1 从task_q获取任务 创建ns ovs_nic 配置nat
# 线程2 间隔30s读取数据库 对时间进行验证 超过360秒的ssh任务放入release_q 与现存ns进行对比 如有差异 任务放入task_q
# 线程3 从release_q 获取任务 删除相关ssh_ns ovs_nic 修改数据库此条status by id

import threading as th
from set_nat import setSshProxyNat



if __name__ == '__main__':
    pass
