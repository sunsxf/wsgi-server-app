#!/usr/bin/env python
# coding=utf-8
# @author sunxiongfei
import re, threading, cgi, json, logging, time
from dboperate import *
from logging_deco import decorator
from io import BytesIO
import os


class MyThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)


class Application():
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        environ, start_response = args
        path = environ['PATH_INFO']
        if path == '/':
            return self.index(environ, start_response)
            # start_response('200 OK', [('Content-Type', 'text/html')])
            # return ['hello'.encode()]
        if path == '/register_or_login':
            return self.choice(environ, start_response)
        if path == '/register_confirm':
            return self.register_confirm(environ, start_response)
        if path == '/login_confirm':
            return self.login(environ, start_response)
        if re.findall(r'/.+?\.jpg', path):
            file_name = re.findall(r'(/)(.+?\.jpg)', path)[0]
            with open(file_name[1], 'rb') as f:
                photo = f.read()
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [photo]
        if re.search(r'^/css.+', path):
            p = re.search(r'^/css.*', path).group()
            filename = p[1:]
            with open(filename) as f:
                css = f.read()
            start_response('200 OK', [('Content-Type', 'text/css')])
            return [css.encode()]
        if re.search(r'^/js.+', path):
            p = re.search(r'^/js.*', path).group()
            filename = p[1:]
            with open(filename) as f:
                js = f.read()
            start_response('200 OK', [('Content-Type', 'text/javascript')])
            return [js.encode()]

        if path == '/request_info':
            return self.rest_api(environ, start_response)
        else:
            return self.notfound(environ, start_response)

    def show_html(self, *args):
        environ, start_response, html = args
        status = '200 ok'
        res_header = [('Content-Type', 'text/html')]
        start_response(status, res_header)
        return [('%s' % html).encode()]

    def index(self, *args):
        environ, start_response = args
        with open('index.html') as f:
            html = f.read()
        return self.show_html(environ, start_response, html)

    def register_html(self, *args):
        environ, start_response = args
        with open('register.html') as f:
            html = f.read()
        return self.show_html(environ, start_response, html)

    def register_confirm(self, *args):
        environ, start_response = args
        # try:
        #     request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        # except:
        #     request_body_size = 0
        # request_body = environ['wsgi.input'].read(request_body_size)
        # print(request_body)
        # environ, start_response = args
        # form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])  # ?  # ?
        # username = form.getvalue('username')
        # password = form.getvalue('password')
        # gender = form.getvalue('gender')
        # district = form.getvalue('district')
        # photo_byte = form.getvalue('photo')
        http = environ.get('HTTP')
        li = []
        p = re.findall(rb'form-data.+?\r\n\r\n(.*?)\r\n', http)
        f = BytesIO(http)
        while True:
            fp = f.readline()
            if b'\xff' and b'\x00' in fp:
                photo_byte = fp
                break
        print(photo_byte)
        for item in p:
            item = item.decode()
            li.append(item)
        username, password, gender, district = li
        print(username)
        photo_path = './%s.jpg' % username
        with open(photo_path, 'wb') as f:
            f.write(photo_byte)
        print('aaaaa')
        mythread = MyThread(insertdb, username, password, gender, district, photo_path)
        mythread.start()
        print()
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['register successfully'.encode('utf-8')]

    def login_html(self, *args):
        environ, start_response = args
        with open('login.html') as f:
            html = f.read()
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [html.encode()]

    def choice(self, *args):
        environ, start_response = args
        query_str = environ['QUERY_STRING']
        if 'login' in query_str:
            return self.login_html(environ, start_response)
        else:
            return self.register_html(environ, start_response)

    def login(self, *args):
        # 已采用AJAX处理
        environ, start_response = args
        # try:
        #     response_body_size = int(environ.get('CONTENT_LENGTH', 0))
        # except:
        #     response_body_size = 0
        # response_body = environ['wsgi.input'].read(response_body_size).decode()
        response_body = environ['wsgi.input']  # 自己写的服务器未把此字段包装成文件句柄
        username = re.findall(r'(username=)(.+)&', response_body)[0][1]
        password = re.findall(r'(password=)(.+)', response_body)[0][1]
        print(username, password)
        try:
            username, password, gender, district, photo_path = query('test', 'regi_info', username, password)
            with open('login_present.html') as f:
                html = f.read()
            # html = html % (username, gender, district, photo_path)
            html = html % (username, gender, district)
            print(username, gender, district)
            start_response('200 OK', [('Content-Type', 'text/html'), ])
            return [html.encode()]
        except Exception as e:
            print('------------', username)
            start_response('200 OK', [('Content-Type', 'text/html'), ])
            return ['ivalid username or password'.encode()]

    def notfound(self, *args):
        environ, start_response = args
        status = '404 not found'
        res_header = [('Content-Type', 'text/html')]
        start_response(status, res_header)
        return [status.encode()]

    @decorator
    def rest_api(self, *args):
        # 从environ中判断请求方法，并取出相关参数（参数错误）
        # 构建返回内容：头部信息，用户请求的信息，以json返回
        environ, start_response = args
        method = environ.get('REQUEST_METHOD')
        logging.debug(method)
        if os.path.exists('cookie'):
            with open('cookie', 'rb') as f:
                content = f.read()
            print('through cookie')
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [content]
        else:
            if method == 'GET':
                query_str = environ['QUERY_STRING']
                logging.debug(query_str)
            else:
                try:
                    response_body_size = int(environ.get('CONTENT_LENGTH', 0))
                except:
                    response_body_size = 0
                query_str = environ['wsgi.input'].read(response_body_size).decode()
            try:
                logging.debug(query_str)
                username = re.search(r'username=(.+)&', query_str).group(1)
                info_num = re.search(r'info_num=(.+)', query_str).group(1)
                # info_num = re.search(r'password=(.+)', query_str).group(1)测试post方法
            except Exception:
                err_num = 502
                e = 'ivalid paras'
                start_response('200 ok', [('Content-Type', 'application/json')])
                return [('{"err_no":%d,"err_msg":"%s"}' % (err_num, e)).encode()]
            try:
                user_info = {}
                info_list = query_api('test', 'regi_info', username, info_num)
                i = 1
                for info in info_list:
                    user, gender, district, photo = info
                    result = {'username': user, 'gender': gender, 'district': district, 'photo': photo}
                    tmp_user_info = {i: result}
                    user_info.update(tmp_user_info)
                    i += 1
                user_info_json = json.dumps(user_info)
                with open('cookie', 'wb') as f:
                    f.write(user_info_json.encode())
                print('no cookie')
            except Exception as e:
                err_num = 501
                start_response('200 ok', [('Content-Type', 'application/json')])
                return [('{"err_no":%d,"err_msg":"%s"}' % (err_num, e)).encode()]
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [user_info_json.encode()]
