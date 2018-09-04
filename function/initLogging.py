#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: initLogging.py
# @time: 2017/10/17 0017 上午 10:03
# @desc:
import logging, os
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger()


def initLog():
    import sys
    global log
    log = logging.getLogger()
    file_name = os.path.abspath(".")+os.sep+"qga_file_io_service"+".log"
    logformatter = logging.Formatter('%(asctime)s [%(levelname)s][%(lineno)05d][%(thread)d] | %(message)s')
    loghandle = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
    loghandle.setFormatter(logformatter)
    loghandle.suffix = '%Y-%m-%d'
    log.addHandler(loghandle)
    # DEBUG < INFO < WARNING < ERROR < CRITICALF
    log.setLevel(logging.WARNING)

initLog()
if __name__ == '__main__':
    log.warning("111111111")
