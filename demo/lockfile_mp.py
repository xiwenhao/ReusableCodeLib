#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: lockfile_mp.py
# @time: 2017/9/27 0027 上午 10:08
# @desc:

# linux
import fcntl


def lock(file_object):
    fcntl.flock(file_object, fcntl.LOCK_EX)


def unlock(file_object):
    fcntl.flock(file_object, fcntl.LOCK_UN)
