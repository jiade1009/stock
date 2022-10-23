#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : base_config.py
# @Description : qmt_client的基本配置
# @Author      : sam
# @Time        : 2022年 10月 21日 16:59
# @Version     : 1.0


# web server配置
web_port = 18022
web_host = "127.0.0.1"

# 签名key
encrypt_keys = {
    "001": "ghk2012",
    "002": "ghk2022"
}
# 当前系统使用的key
encrypt_current_key = "001"
# 时间戳有效期 60s
encrypt_interval = 60


# qmt交易客户端API地址
qmt_client_api = "http://192.168.0.103:18012"
# qmt_client_api = "http://127.0.0.1:18012"
qmt_request_a_buy = "/stock/a_buy"
qmt_request_a_buy_result = "/stock/a_buy_result"


# log file
log_file = "/Users/sam/Documents/IdeaProjects/stock/qmtserver/log.txt"


