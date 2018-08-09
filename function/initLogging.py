#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: initLogging.py
# @time: 2017/10/17 0017 上午 10:03
# @desc:
import logging
from logging.handlers import TimedRotatingFileHandler

log = logging.getLogger()


def initLog():
    import sys
    global log
    file_name = sys.argv[0][0:-3] + ".log"
    logformatter = logging.Formatter('%(asctime)s [%(levelname)s][%(lineno)05d][%(thread)d] | %(message)s')
    loghandle = TimedRotatingFileHandler(file_name, 'midnight', 1, 2)
    loghandle.setFormatter(logformatter)
    loghandle.suffix = '%Y-%m-%d'
    log.addHandler(loghandle)
    # DEBUG < INFO < WARNING < ERROR < CRITICAL
    log.setLevel(logging.INFO)

initLog()
if __name__ == '__main__':
    log.warning("111111111")
