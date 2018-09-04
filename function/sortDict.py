#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 14:09
# @Author  : xwh
# @File    : sortDict.py

# d = {
#     "q": (5, 3),
#     "w": (4, 4),
#     "e": (2, 2),
#     "r": (1, 5)
# }
# # 整个字典被转换成了两元素元组(k, v),匿名函数中的x后第一个[1]表示原来字典中的v v也被转换成了元组第二个[0]表示v转换成的元组中第一个元素
# # 按元组左侧元素排列
# print sorted(d.iteritems(),key=lambda x:x[1][0], reverse=True)
# # [('q', (5, 3)), ('w', (4, 4)), ('e', (2, 2)), ('r', (1, 5))]
#
# # 按元组右侧元素排列
# print sorted(d.iteritems(),key=lambda x:x[1][1], reverse=True)
# # [('r', (1, 5)), ('w', (4, 4)), ('q', (5, 3)), ('e', (2, 2))]


d = {
    "q": {
        "a": 1,
        "b": 2
    },
    "w": {
        "a": 6,
        "b": 3
    },
    "e": {
        "a": 2,
        "b": 8
    },
    "r": {
        "a": 3,
        "b": 1
    }
}
# lambda 返回一个可以进行排序的元素(数字或字符)
print sorted(d.iteritems(), key=lambda x: x[1]["a"], reverse=True)
print ""
print sorted(d.iteritems(), key=lambda x: x[1]["b"], reverse=True)
