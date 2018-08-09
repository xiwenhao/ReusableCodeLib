#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/14 16:34
# @Author  : xwh
# @File    : useVideoCapture.py
# import VideoCapture
#
# device = VideoCapture.Device()
# img = device.getImage()
#
# print type(img), img
import VideoCapture

cam = VideoCapture.Device(devnum=0)
cam.saveSnapshot('test.jpg', quality=75, timestamp=3, boldfont=1)
'''
Traceback (most recent call last):
  File "E:/Share/otherPYcode/opencv/useVideoCapture.py", line 15, in <module>
    cam.saveSnapshot('test.jpg', quality=75, timestamp=3, boldfont=1)
  File "D:\anaconda2\lib\site-packages\VideoCapture\__init__.py", line 234, in saveSnapshot
    self.getImage(timestamp, boldfont, textpos).save(filename, **keywords)
  File "D:\anaconda2\lib\site-packages\VideoCapture\__init__.py", line 154, in getImage
    'RGB', (width, height), buffer, 'raw', 'BGR', 0, -1)
  File "D:\anaconda2\lib\site-packages\PIL\Image.py", line 2337, in fromstring
    "Please call frombytes() instead.")
NotImplementedError: fromstring() has been removed. Please call frombytes() instead.
'''