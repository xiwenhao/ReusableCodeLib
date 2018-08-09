#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: aboutTkinter.py
# @time: 2017/11/27 0027 下午 5:20
# @author: xwh
# @desc:

from Tkinter import *


root = Tk()
root.title("first GUI")
root.geometry("500x100")
root.resizable(width=False, height=True)

lang = ['c','java','php','python']
movie = ['css','jQ','Bs']
listb = Listbox(root, width=10)
listb2 = Listbox(root,  width=50)
for item in lang:
    listb.insert(0, item)
for item in movie:
    listb2.insert(0,item)
listb.pack(side=LEFT)
listb2.pack(side=RIGHT)

root.mainloop()