#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: aboutYield.py
# @time: 2017/10/20 0020 下午 4:19
# @desc:
import itertools

def mygen():
    for i in xrange(1000):
        yield i**2


if __name__ == '__main__':
    # 生成器可以看做是类 需要实例化
    print type(mygen())

