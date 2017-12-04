#!/usr/bin/env python
# coding=utf-8
# @author sunxiongfei
import pymysql


class DbOperate():
    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def dbconnect(self, dbname):
        db = pymysql.connect(self.host, self.user, self.password, dbname)
        return db

    def create_table(self, dbname, tablename):
        db = self.dbconnect(dbname)
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS %s" % tablename)
        sql = '''
        CREATE TABLE %s (
        username CHAR(255) NOT NULL,
        password CHAR(255) NOT NULL,
        gender CHAR(255) NOT NULL,
        district CHAR(255) NOT NULL,
        photo_path CHAR(255) NOT NULL
        )''' % tablename
        cursor.execute(sql)

    def insert_info(self, dbname, table_name, register_info):
        db = self.dbconnect(dbname)
        cursor = db.cursor()
        sql = "INSERT INTO %s" % table_name + "(username,password,gender,district,photo_path) VALUES('%s','%s','%s','%s','%s')" % register_info
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
        db.close()

    def query_info(self, dbname, table_name, username, password):
        db = self.dbconnect(dbname)
        cursor = db.cursor()
        sql = "SELECT * FROM %s WHERE username = '%s' AND password = '%s'" % (table_name, username, password)
        try:
            cursor.execute(sql)
            result = cursor.fetchall()[0]
            return result
        except:
            return 'ivalid username or password'

    def query_api(self, dbname, table_name, username, info_num):
        db = self.dbconnect(dbname)
        cursor = db.cursor()
        sql = "SELECT * FROM %s WHERE username = '%s'" % (table_name, username)
        cursor.execute(sql)
        result = cursor.fetchall()
        if result:
            info_list = []
            sql = "SELECT * FROM %s LIMIT %s" %(table_name,info_num)
            cursor.execute(sql)
            result = cursor.fetchall()
            for i in result:
                info = list(i)
                del info[1]
                info_list.append(info)
            return info_list
        else:
            raise Exception('ivalid username or info_num')



def get_info(*args):
    return args


def insertdb(username, password, gender, district, photo_path):
    db_instance = DbOperate('localhost', 'root', '123456')
    #db_instance.create_table('test', 'regi_info')
    db_instance.insert_info('test', 'regi_info', get_info(username, password, gender, district, photo_path))


def query(dbname, table_name, username, password):
    db_instance = DbOperate('localhost', 'root', '123456')
    result = db_instance.query_info(dbname, table_name, username, password)
    return result


def query_api(dbname, table_name, username,num):
    db_instance = DbOperate('localhost', 'root', '123456')
    result = db_instance.query_api(dbname, table_name, username,num)
    return result
