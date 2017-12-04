#!/usr/bin/env python
# coding=utf-8
# @author sunxiongfei
import socket
import threading
from threadpool import *
import json, time, queue, asyncio

headers = '''GET /sun.jpg HTTP/1.1\r\n
            Host: 127.0.0.1:9999\r\n
            Connection: keep-alive\r\n
            Cache-Control: max-age=0\r\n
            User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36\r\n
            Upgrade-Insecure-Requests: 1\r\n
            Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n
            Accept-Encoding: gzip, deflate, br\r\n
            Accept-Language: en-US,en;q=0.9\r\n'''


async def send_req():
    for _ in range(100):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(('127.0.0.1', 9999))
        conn.send(headers.encode())
        print('sending')
        await recv_res(conn)


async def recv_res(conn):
    data = conn.recv(1024)
    print('receiving')
    while True:
        data_ = conn.recv(1024)
        data += data_
        if not data_:
            conn.close()
            break


t1 = time.time()
loop = asyncio.get_event_loop()
tasks = [send_req()]
loop.run_until_complete(asyncio.wait(tasks))
t2 = time.time()
loop.close()
print(t2 - t1)
