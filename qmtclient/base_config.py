#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : base_config.py
# @Description : qmt_client的基本配置
# @Author      : sam
# @Time        : 2022年 10月 21日 16:59
# @Version     : 1.0


# web server配置
web_port = 18012
web_host = "127.0.0.1"
# web_host = "192.168.0.103"

# 签名key
encrypt_key = "ghk2012"
encrypt_idx = "001"
# 时间戳有效期 60s
encrypt_interval = 60


# qmt 股票账号
qmt_account = "55002178"
# qmt文件路径
qmt_file_path = "/Users/sam/data/stock/qmt/"
# qmt_file_path = "D:\\program\\国金QMT交易端模拟\\export_data\\"
# buy_order文件名
qmt_file_buy_order = "XT_DBF_ORDER.dbf"
# buy_order_result文件名
qmt_file_buy_order_result = "XT_DBF_ORDER_result.dbf"
# buy_order 字段定义
qmt_file_buy_order_columns = """
order_type C(10); price_type C(10); mode_price C(10); stock_code C(10); volume C(10); account_id C(10); act_type C(10);
brokertype C(10); strategy C(50); note C(100); tradeparam C(100); inserttime C(30);
"""


# log_file
log_file = "/Users/sam/Documents/IdeaProjects/stock/qmtclient/log.txt"
# log_file = "D:\\hkfund\program\\qmt_client\\qmtclient\\log.txt"



