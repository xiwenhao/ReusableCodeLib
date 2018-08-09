#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/14 10:16
# @Author  : xwh
# @File    : useOpenCv.py
# face-recognition-models


import cv2
import cv2.cv as cv
import time
from face_recognition_models import *
#
# cap = cv2.VideoCapture(0)
# fourcc = cv2.cv.CV_FOURCC(*'XVID')
# # out = cv2.VideoWriter('output.avi',fourcc,20.0,(640,480))#保存视频
# while True:
#     ret,frame = cap.read()
#     gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
#     # out.write(frame)#写入视频
#     cv2.imshow('frame',frame)#一个窗口用以显示原视频
#     cv2.imshow('gray',gray)#另一窗口显示处理视频
#
#
#     if cv2.waitKey(1) &0xFF == ord('q'):
#         break
#
# cap.release()
# out.release()
# cv2.destroyAllWindows()

# gray_photo = cv2.cvtColor(cap, cv2.COLOR_BGR2BGRA)
#
# cv2.imshow("Image Title",gray_photo)
# time.sleep(30)

cap = cv2.VideoCapture(0)
while True:
    cv2.waitKey(10)
    ret,frame = cap.read()
    gray = cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)
    # out.write(frame)#写入视频
    cv2.imshow('frame',frame)#一个窗口用以显示原视频
    cv2.imshow('gray',gray)#另一窗口显示处理视频


