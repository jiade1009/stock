#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : dbf_utils.py
# @Description : TODO
# @Author      : sam
# @Time        : 2022年 10月 21日 11:34
# @Version     : 1.0
import pandas as pd
import dbf
import dbfread
import os
import datetime
from qmtclient import base_config
from qmtclient.logUtils import logger

qmt_file_path = base_config.qmt_file_path
if not os.path.exists(qmt_file_path):
    os.makedirs(qmt_file_path)  # 创建多个文件夹结构。


def w_a_buy_file(stock_list: list):
    """
    保存买进信息，文件格式dbf
    采用记录追加的模式写入文件
    :param stock_list:
    :return:
    """
    filename = base_config.qmt_file_path + base_config.qmt_file_buy_order
    if not os.path.exists(filename):
        table = dbf.Table(filename=filename, field_specs=base_config.qmt_file_buy_order_columns, codepage='cp936')
    else:
        table = dbf.Table(filename=filename, codepage='cp936')  # 相当于gbk的方式打开
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    with table:
        # 修改为读写模式
        table.open(mode=dbf.READ_WRITE)
        # 添加数据
        """
        order_type C(10); price_type C(10); mode_price C(10); stock_code C(10); volume C(10); account_id C(10); 
        act_type C(10); brokertype C(10); strategy C(10); note C(10); tradeparam C(10); inserttime C(10)
        item = ('23', '1', '', stock_code, 100, base_config.qmt_account, '', '2', '纯阳信号下单', '自有资金', '', now_str)
        """
        for item in stock_list:
            # item 数据格式：
            record = ('23', '3', item['price'], item['code'], item['amount'], base_config.qmt_account, '', '2',
                      item['hold_trade_id'], item['hold_trade_id'], '', now_str)
            table.append(record)


def r_a_buy_result_file():
    """
    读取买入结果文件，文件格式dbf
    0 - ORDERID 1 - MESSAGE 2 - STATUS 3 - NOTE  4 - TASKID    5 - TASKSTATUS6 - TASKMSG   7 - TASKPRO   8 - ORDERNUM
    :return:
    """
    filename = base_config.qmt_file_path + base_config.qmt_file_buy_order_result
    if not os.path.exists(filename):
        logger.error("文件不存在:%s", filename)
        return -1
    else:
        # table = dbf.Table(filename=filename, codepage='cp936')  # 相当于gbk的方式打开
        table = dbfread.DBF(filename=filename, encoding='gbk', load=True)  # 采用dbfread
        result_list = []
        with table:
            for row in table:
                result_list.append(list(row.values()))
        return result_list


def r_a_buy_result_by_orderid(orderid):
    """
    读取买入结果文件，文件格式dbf
    0 - ORDERID   1 - MESSAGE   2 - STATUS    3 - NOTE      4 - TASKID    5 - TASKSTATUS6 - TASKMSG   7 - TASKPRO   8 - ORDERNUM
    :param orderid:
    :return:
    """
    filename = base_config.qmt_file_path + base_config.qmt_file_buy_order_result
    if not os.path.exists(filename):
        logger.error("文件不存在:%s", filename)
        return -1
    else:
        table = dbfread.DBF(filename=filename, encoding='gbk')  # 采用dbfread
        result_list = []
        with table:
            for row in table:
                if row["orderid"] == orderid:
                    return list(row.values)
        return None

def write_file(filename: str):
    # 创建test.dbf文件 共两列 name 字符串 长度25；age 数值 长度3
    table = dbf.Table(filename=filename, field_specs=base_config.qmt_file_buy_order_columns, codepage='cp936')
    # 修改为读写模式
    table.open(mode=dbf.READ_WRITE)
    # 添加数据
    now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    record = ('23', '3', '10', '000010', '100', base_config.qmt_account, '', '2',
              '纯阳信号下单', '自有资金', '', now_str)
    table.append(record)
    table.close()


def read_file(filename: str):
    if os.path.isfile(filename):
        table = dbf.Table(filename=filename, codepage='cp936')
    else:
        table = dbf.Table(filename=filename, field_specs=base_config.qmt_file_buy_order_columns, codepage='cp936')
    with table:
        for row in table:
            print(row)
    # table.open(mode=dbf.READ_WRITE)


if __name__ == '__main__':
    # f_name = base_config.qmt_file_path + base_config.qmt_file_buy_order
    # f_name_result = base_config.qmt_file_path + base_config.qmt_file_buy_order_result
    # # write_file(f_name)
    # read_file(f_name)
    # read_file(f_name_result)
    r_a_buy_result_file()
