#!/usr/bin/env python
# coding=utf-8
# @author sunxiongfei
import socket, threading, re, os, datetime, selectors, asyncio, cgi, time
from appClass import Application
import threading
from multiprocessing import Pool

local_status = threading.local()
local_res_header = threading.local()
CHUNK = 1024*100
headers = '''HTTP/1.0 200 OK
                        Server: WSGIServer/0.2 CPython/3.5.2
                        Content-Type: text/html
                        Content-Length: %d
                        Connection: Keep-Alive
                        Pragma: no-cache\r\n\r\n'''


class MyWsgiSever():
    def __init__(self, host, port, app):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        self.app = app

    async def handle_req(self, conn):
        http = conn.recv(CHUNK)
        p = re.search(r'(GET) /(.*?html.*|.+?css|.+?js|.+?jpg|.?) HTTP', http.decode())
        try:
            if p:
                print(1)
                path_ = p.group(2)
                if path_ == '':  # 访问索引页
                    with open('index.html') as f:
                        content = f.read()
                        length = len(content)
                        conn.send((headers % length + content).encode())
                        # time.sleep(100000000)
                else:  # 请求相应的静态文件
                    try:
                        path = path_.split('?')[0]
                        query_str = path_.split('?')[1]
                    except Exception as e:  # 处理CSS，JS文件文件路径
                        path = path_  #
                    if 'jpg' in path:  # 请求图片
                        with open(path, 'rb') as f:
                            content = f.read()
                            length = len(content)
                        conn.send((headers % length).encode() + content)
                    else:
                        try:
                            with open(path, 'r') as f:  # 请求CSS，JS，静态HTML
                                content = f.read()
                                length = len(content)
                            conn.send((headers % length + content).encode())
                        except:
                            conn.send((headers % 13 + '404 NOT FOUND').encode())
                conn.close()
            else:  # 请求应用程序,只有POST方法
                print(2)
                p = re.search(r'(POST) (/.*?) HTTP', http.decode())
                method = p.group(1)
                path = p.group(2)
                try:  # 无图片上传
                    form_data = re.search(r'\r\n\r\n(.+)', http.decode()).group(1)
                    len_data = len(form_data)
                    environ = {'REQUEST_METHOD': method,
                               'PATH_INFO': path,
                               'wsgi.input': form_data,
                               'CONTENT_LENGTH': len_data}
                except:  # 图片上传
                    print(4)
                    content = conn.recv(CHUNK)
                    environ = {'REQUEST_METHOD': method,
                               'PATH_INFO': path,
                               'HTTP': http + content}
                data = self.app(environ, self.start_response)
                self.putback_to_client(data, conn)
        except Exception as e:
            print('=================', e)
            conn.close()

    def start_response(self, status, res_header):
        self.status = status
        self.res_header = res_header

    def putback_to_client(self, data, conn):
        try:
            response = 'HTTP/1.1 %s\r\n' % self.status
            for header in self.res_header:
                response += '%s: %s\r\n' % (header[0], header[1])
            response += '\r\n'
            data_ = data[0]  # 应用程序返回值和start_response回调函数的header都是以列表形式返回
            response += data_.decode()
            conn.send(response.encode())
        finally:
            conn.close()

    async def accept_conn(self):
        while True:
            try:
                conn, addr = self.sock.accept()
                print('accept connection from ', str(addr))
                await self.handle_req(conn)
                # 到await的时候直接进入下一个co,直到await的函数返回
            except Exception as e:
                print('------------------------------', e)

    def make_server(self):
        loop = asyncio.get_event_loop()
        tasks = [self.accept_conn()]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()


server = MyWsgiSever('', 9999, Application())
server.make_server()
# 3300,4900,8800
