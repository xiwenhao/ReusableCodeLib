#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/13 9:25
# @Author  : xwh
# @File    : wangyiyun.py
# 本人不建议通过该手段获取版权音乐/MV，为了你喜爱的歌手请尊重他人劳动成果，支持正版！

import os


cache_dir = "d:/Cache"

d = os.walk(cache_dir)
file_list = next(d)[2]
for each_file in file_list:
    if ".uc" not in each_file:
        continue
    else:
        with open("d:/Cache/"+each_file, "rb") as f:
            with open("d:/Cache/"+each_file+".mp3", "wb") as q:
                for i in list(f.read()):
                    data = ord(i) ^ 0xa3
                    q.write(chr(data))
        print "done", each_file

# import eyed3
# file_path = "d:/26423114-320-a2dab8d9985ebb3bf5708166f7102e51.uc.mp3"

# _file = eyed3.load(file_path)
# print _file.tag.album

# import eyed3
#
# audiofile = eyed3.load("song.mp3")
# audiofile.tag.artist = u"Nobunny"
# audiofile.tag.album = u"Love Visions"
# audiofile.tag.album_artist = u"Various Artists"
# audiofile.tag.title = u"I Am a Girlfriend"
# audiofile.tag.track_num = 4
# audiofile.tag.save()