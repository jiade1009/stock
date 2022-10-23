#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : server_request_client.py
# @Description : 服务端请求qmt交易客户端
# @Author      : sam
# @Time        : 2022年 10月 21日 15:25
# @Version     : 1.0
import json

import requests

from qmtserver import base_config
from qmtserver import encrypt
from qmtserver.logUtils import logger


def request_buy(stock_list: list) -> dict:
    params = {
        "data": stock_list,
        "method": "a_buy"
    }
    params = encrypt.do_encrypt(params, base_config.encrypt_current_key)
    url = base_config.qmt_client_api + base_config.qmt_request_a_buy
    logger.info("请求体 params ={}".format(params))
    res = requests.post(url=url, data=json.dumps(params))
    logger.info("返回值:{}".format(json.loads(res.content)))
    result = json.loads(res.content)
    return result


def request_buy_result() -> dict:
    """
    请求获取qmt股票交易结果记录
    1.发起请求
    :return:
    """
    params = {
        "data": {},
        "method": "a_buy_result"
    }
    params = encrypt.do_encrypt(params, base_config.encrypt_current_key)
    url = base_config.qmt_client_api + base_config.qmt_request_a_buy_result
    logger.info("请求体 params ={}".format(params))
    res = requests.post(url=url, data=json.dumps(params))

    result = json.loads(res.content)
    logger.info("返回值:{}".format(json.loads(res.content)))
    return result


if __name__ == "__main__":
    # stocks = [{'hold_id': '12', 'code': '000735', 'amount': '100', 'price': '10'},
    #           {'hold_id': '16', 'code': '002035', 'amount': '200', 'price': '20'},
    #           {'hold_id': '15', 'code': '600909', 'amount': '500', 'price': '30'}]
    # request_buy(stocks)

    r_list = request_buy_result()
    logger.info(r_list)
