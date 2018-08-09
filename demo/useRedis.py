#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: useRedis.py
# @time: 2017/10/20 0020 下午 3:08
# @desc: Hiredis 是由 Redis 核心团队维护的 C 库。 Pieter Noordhuis 创建了 Python 的实现。
# 分析 Redis 服务器的响应时，Hiredis 可以提供 10 倍的速度提升。 pip install hiredis

import redis

# 使用连接池避免额外开销
connect_pool = redis.ConnectionPool(host="127.0.0.1", port=6379)

redis_connect = redis.StrictRedis(connection_pool=connect_pool)
redis_connect.set("foo", "bar")
redis_connect.rpush("mylist", "one")
print redis_connect.get("foo")
print "\n", redis_connect.rpop("mylist")

# 使用pipeline一次性执行多个操作 避免多次往返延迟, transaction=False 取消pipe的原子性
pipe = redis_connect.pipeline(transaction=False)
pipe.set("one", "first")
pipe.set("two", "second")
pipe.execute()
#  等价
pipe.set('one', 'first').rpush('list', 'hello').rpush('list', 'world').execute()


