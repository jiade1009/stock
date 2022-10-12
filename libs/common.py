#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# apk add py-mysqldb or

import platform
import datetime
import time
import sys
import os
import MySQLdb
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR
from sqlalchemy import inspect
import pandas as pd
import traceback
import akshare as ak
from log.logUtils import logger
import libs.basic_conf as basic_conf

# 使用环境变量获得数据库。兼容开发模式可docker模式。
MYSQL_HOST = os.environ.get('MYSQL_HOST') if (os.environ.get('MYSQL_HOST') is not None) else basic_conf.cfg_mysql_host
MYSQL_USER = os.environ.get('MYSQL_USER') if (os.environ.get('MYSQL_USER') is not None) else basic_conf.cfg_mysql_user
MYSQL_PWD = os.environ.get('MYSQL_PWD') if (os.environ.get('MYSQL_PWD') is not None) else basic_conf.cfg_mysql_pwd
MYSQL_DB = os.environ.get('MYSQL_DB') if (os.environ.get('MYSQL_DB') is not None) else basic_conf.cfg_mysql_db

logger.debug("MYSQL_HOST :%s, MYSQL_USER :%s, MYSQL_DB :%s", MYSQL_HOST, MYSQL_USER, MYSQL_DB)
MYSQL_CONN_URL = "mysql+mysqldb://" + MYSQL_USER + ":" + MYSQL_PWD + "@" + MYSQL_HOST + ":3306/" + MYSQL_DB + "?charset=utf8mb4"
logger.info("MYSQL_CONN_URL : %s", MYSQL_CONN_URL)

__version__ = "2.0.0"
# 每次发布时候更新。


def engine():
    return create_engine(MYSQL_CONN_URL, encoding='utf8', convert_unicode=True)


def engine_to_db(to_db):
    MYSQL_CONN_URL_NEW = "mysql+mysqldb://" + MYSQL_USER + ":" + MYSQL_PWD + "@" + MYSQL_HOST + ":3306/" + to_db \
                         + "?charset=utf8mb4"
    # echo = True 是为了方便 控制台 logging 输出一些sql信息，默认是False
    return create_engine(MYSQL_CONN_URL_NEW, encoding='utf8', convert_unicode=True, echo=True)


def conn():
    # 通过数据库链接 engine。
    try:
        db = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PWD, MYSQL_DB, charset="utf8")
        # db.autocommit = True
    except Exception as e:
        logger.error("conn error : %s %s", e.__class__.__name__, e)
    db.autocommit(on=True)
    return db.cursor()


def insert_db(data, table_name, write_index, primary_keys):
    """
    定义通用方法函数，插入数据库表，并创建数据库主键，保证重跑数据的时候索引唯一。
    :param data: 插入的数据，数据类型为dataframe
    :param table_name: 操作的数据表
    :param write_index: Write DataFrame index as a column
    :param primary_keys: 主键字段
    :return:
    """
    # 插入默认的数据库
    insert_other_db(MYSQL_DB, data, table_name, write_index, primary_keys)


def insert_other_db(to_db, data, table_name, write_index, primary_keys):
    """
    增加一个插入到其他数据库的方法
    :param to_db: 数据库名
    :param data: 插入的数据，数据类型为dataframe
    :param table_name: 操作的数据表
    :param write_index: Write DataFrame index as a column
    :param primary_keys: 主键字段
    :return:
    """
    # 定义engine
    engine_mysql = engine_to_db(to_db)
    # 使用 http://docs.sqlalchemy.org/en/latest/core/reflection.html
    # 使用检查检查数据库表是否有主键。
    my_inspect = inspect(engine_mysql)
    col_name_list = data.columns.tolist()
    # 如果有索引，把索引增加到varchar上面。
    if write_index:
        # 插入到第一个位置：
        col_name_list.insert(0, data.index.name)
    data.to_sql(name=table_name, con=engine_mysql, schema=to_db, if_exists='append',
                dtype={col_name: NVARCHAR(length=255) for col_name in col_name_list}, index=write_index)

    # print(my_inspect.get_pk_constraint(table_name))
    # 判断是否存在主键
    if not my_inspect.get_pk_constraint(table_name)['constrained_columns']:
        with engine_mysql.connect() as con:
            # 执行数据库插入数据。
            try:
                con.execute('ALTER TABLE `%s` ADD PRIMARY KEY (%s);' % (table_name, primary_keys))
            except Exception as e:
                logger.error("################## ADD PRIMARY KEY ERROR : %s %s", e.__class__.__name__, e)


def insert(sql, params=()):
    """
    插入数据。
    :param sql:
    :param params: 元祖类型
    :return:
    """
    with conn() as db:
        logger.info("insert sql: %s", sql)
        try:
            db.execute(sql, params)
        except Exception as e:
            logger.error("insert sql error :%s %s", e.__class__.__name__, e)


def insert_batch(sql, params=[()]):
    """
    批量插入数据。
    :param sql:
    :param params: 传递元祖类型的list集合
    :return:
    """
    with conn() as db:
        logger.info("insert sql: %s", sql)
        try:
            db.executemany(sql, params)
        except Exception as e:
            logger.error("insert sql error :%s %s", e.__class__.__name__, e)


def select(sql, params=()):
    """
    查询数据
    :param sql:
    :param params:
    :return:
    """
    with conn() as db:
        logger.info("select sql:%s", sql)
        try:
            db.execute(sql, params)
        except Exception as e:
            logger.error("select sql error :%s %s", e.__class__.__name__, e)
        result = db.fetchall()
        return result


def select_count(sql, params=()) -> int:
    """
    计算数量
    :param sql:
    :param params:
    :return:
    """
    with conn() as db:
        logger.info("select_count sql:%s", sql)
        try:
            db.execute(sql, params)
        except Exception as e:
            logger.error("select_count sql error :%s %s", e.__class__.__name__, e)
        result = db.fetchall()
        # 只有一个数组中的第一个数据
        if len(result) == 1:
            return int(result[0][0])
        else:
            return 0


def run_with_args(run_fun):
    """
    通用函数：根据调用py所对应的参数，获得日期参数和迭代数值。
    3种传递参数格式：
    1. python xxx.py 2017-07-01 10：指定要调用的日期，以及递归循环调用前10日的数据
    2. python xxx.py 2017-07-01：调用指定的日期
    3. python xxx.py ：调用当天的日期
    :param run_fun: 回调函数名
    :return:
    """
    tmp_datetime_show = datetime.datetime.now()  # 修改成默认是当日执行 + datetime.timedelta()
    tmp_hour_int = int(tmp_datetime_show.strftime("%H"))
    if tmp_hour_int < 12:
        # 判断如果是每天 中午 12 点之前运行，跑昨天的数据。
        tmp_datetime_show = (tmp_datetime_show + datetime.timedelta(days=-1))
    tmp_datetime_str = tmp_datetime_show.strftime("%Y-%m-%d %H:%M:%S.%f")
    logger.info("######################### hour_int %d " % tmp_hour_int)
    logger.info("######################### begin run %s %s  #########################" % (run_fun, tmp_datetime_str))
    start = time.time()
    # 要支持数据重跑机制，将日期传入。循环次数
    if len(sys.argv) == 3:
        # python xxx.py 2017-07-01 10
        tmp_year, tmp_month, tmp_day = sys.argv[1].split("-")
        loop = int(sys.argv[2])
        tmp_datetime = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day))
        for i in range(0, loop):
            # 循环插入多次数据，重复跑历史数据使用。
            # time.sleep(5)
            tmp_datetime_new = tmp_datetime + datetime.timedelta(days=i)
            try:
                run_fun(tmp_datetime_new)
            except Exception as e:
                logger.error("select sql error :%s %s", e.__class__.__name__, e)
                traceback.print_exc()
    elif len(sys.argv) == 2:
        # python xxx.py 2017-07-01
        tmp_year, tmp_month, tmp_day = sys.argv[1].split("-")
        tmp_datetime = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day))
        try:
            run_fun(tmp_datetime)
        except Exception as e:
            logger.error("select sql error :%s %s", e.__class__.__name__, e)
            traceback.print_exc()
    else:
        try:
            run_fun(tmp_datetime_show)  # 使用当前时间
        except Exception as e:
            logger.error("select sql error :%s %s", e.__class__.__name__, e)
            traceback.print_exc()
    logger.info("######################### finish %s , use time: %s #########################" % (
        tmp_datetime_str, time.time() - start))


# 设置基础目录，每次加载使用。
bash_stock_tmp = basic_conf.cfg_stock_history_tmp
if not os.path.exists(bash_stock_tmp):
    os.makedirs(bash_stock_tmp)  # 创建多个文件夹结构。
    logger.info("######################### init tmp dir #########################")


def get_hist_data_cache(code, date_start, date_end):
    """
    增加读取股票缓存方法。加快处理速度
    :param code:
    :param date_start:
    :param date_end:
    :return:
    """
    cache_dir = bash_stock_tmp % (date_end[0:6], date_end)
    # 如果没有文件夹创建一个。月文件夹和日文件夹。方便删除。
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_file = cache_dir + "%s^%s.gzip.pickle" % (date_end, code)
    # 如果缓存存在就直接返回缓存数据。压缩方式。
    if os.path.isfile(cache_file):
        logger.info("######### read from cache %s #########" % cache_file)
        return pd.read_pickle(cache_file, compression="gzip")
    else:
        logger.info("######### get data, write cache ######### %s %s %s" % (code, date_start, date_end))
        stock = ak.stock_zh_a_hist(symbol=code, start_date=date_start, end_date=date_end, adjust="")
        if stock.empty:
            return None
        stock.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'quote_change',
                         'ups_downs', 'turnover']
        stock = stock.sort_index(axis=0)  # 将数据按照日期排序下。
        # print(stock)
        stock.to_pickle(cache_file, compression="gzip")
        return stock
