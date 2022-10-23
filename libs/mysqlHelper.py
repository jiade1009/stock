#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : mysqlHelper.py
# @Description : TODO
# @Author      : sam
# @Time        : 2022年 10月 22日 22:40
# @Version     : 1.0
import traceback
import pymysql
from dbutils.pooled_db import PooledDB


class MySQLhelper(object):
    def __init__(self, host, port, dbuser, password, database):
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=3,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，
            # 所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested,
            # 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=host,
            port=int(port),
            user=dbuser,
            password=password,
            database=database,
            charset='utf8'
        )

    def create_conn_cursor(self):
        conn = self.pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        return conn, cursor

    def fetch_all(self, sql, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            cursor.execute(sql, args)
            res = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())
        return res

    def insert_one(self, sql, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            res = cursor.execute(sql, args)
            conn.commit()
            print("记录数:" + str(res))
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())
        return res

    def insert_batch(self, sql, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            res = cursor.executemany(sql, args)
            conn.commit()
            print("记录数:" + str(res))
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())
        return res

    def update(self, sql, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            res = cursor.execute(sql, args)
            conn.commit()
            print("记录数:" + str(res))
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())
        return res

    def delete(self, sql, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            res = cursor.execute(sql, args)
            conn.commit()
            print("记录数:" + str(res))
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())
        return res

    # 存储函数调用(无返回值 ,增删改)
    # 参数格式 args=(1, 2, 3, 0)
    def mfunctionVo(self, name, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            cursor.callproc(name, args)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())

    # 存储函数调用(有返回值,查)
    # 参数格式 args=(1, 2, 3, 0)
    def mfunctionRe(self, name, args=None):
        try:
            conn, cursor = self.create_conn_cursor()
            cursor.callproc(name, args)
            conn.commit()
            res = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception:
            print(traceback.format_exc())
        return res


if __name__ == '__main__':

    sqlhelper = MySQLhelper("192.168.42.136", 3306, "root", "root", "ip_pool")

    rest = sqlhelper.fetch_all("select `ip`,`port` from ip_pool_new ")

    for i in rest:
        print(rest)
    # sqlhelper.mfunctionVo("deWeight")

# sqlhelper.fetch_all("select * from user where id=%s",(1))

# sqlhelper.insert_one("insert into user VALUES (%s,%s)",("jinwangba",4))

# sqlhelper.update("update user SET name=%s WHERE  id=%s",("yinwangba",1))
