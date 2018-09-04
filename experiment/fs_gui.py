#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/24 14:26
# @Author  : xwh
# @File    : fs_gui.py
import tkinter
from tkinter import filedialog
from Tkinter import *
root = Tk()
root.title("upload file")
root.geometry('600x400')
local_dir_list = ["c:\\qqqqqqqqqq\\qxxxxxx\\yyyyyy", "afasfasef", "asdfasefasefasef", "adsfaefasef"]



def choice_dir():
    #  filedialog.askopenfilename(title='打开文件', filetypes=[('Python', '*.py *.pyw'), ('All Files', '*')])
    dir_path = filedialog.askdirectory(title='choice dir')
    local_dir_list.append(dir_path)
    text.insert('1.0', "%s\n" % dir_path)
    print dir_path
    text.update()


root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


text=Text(root,width=20,height=20)
text.pack(fill=X,side=BOTTOM  )
# text.insert(END, 'this Row finished...\n')  # INSERT表示在光标位置插入
text.see(END)
for d in local_dir_list:
    text.insert('1.0', "%s\n" % d)
    text.update()

btn1 = Button(root, text='choice dir', command=choice_dir)
btn2 = Button(root, text='upload', command=choice_dir)
# selected_show = tkinter.
# btn2 = tkinter.Button(root, text='File Save', command=savefile)

btn1.pack(side='left')
btn2.pack(side='right')
# btn2.pack(side='left')
root.mainloop()