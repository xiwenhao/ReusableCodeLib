#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/11 17:28
# @Author  : xwh
# @File    : getAbsPath.py

import os
import sys


filename = sys.argv[0].split(os.sep)[-1]
print os.path.abspath(os.path.curdir), filename
print os.sep