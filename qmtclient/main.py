#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""终端执行某个文件的时候都是直接运行指定文件的，缺少需要检索的路径，需要将我们自定义的模块路径引入"""
# 调用os，sys模块
import os
import sys
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath或者os.path.dirname(__file__)))
# BASE_DIR2 = os.path.abspath(os.path.join(os.getcwd(), ".."))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

# @Name        : main.py
# @Description : qmt 批量埋单 服务接口
# @Author      : sam
# @Time        : 2022年 10月 21日 12:32
# @Version     : 1.0
import datetime

import flask
import json

from qmtclient import base_config
from qmtclient.logUtils import logger
from flask import request
from qmtclient import encrypt
from qmtclient import dbf_utils


'''
flask： web框架，通过flask提供的装饰器@server.route()将普通函数转换为服务
登录接口，需要传url、username、passwd
'''
# 创建一个服务，把当前这个python文件当做一个服务
server = flask.Flask(__name__)


@server.route('/stock/a_buy', methods=['post'])
def stock_a_buy():
    # 获取通过url请求传参的数据
    # name = request.args.get('name')
    data = json.loads(request.data)
    logger.info("请求体的数据:%s" % data)

    # 校验数据
    check_int = encrypt.check_encrypt(data)
    if check_int == 0:
        # 创建dbf文件
        # logger.info("stock list: %s" % data['data'])
        dbf_utils.w_a_buy_file(data['data'])
        res = {'status': 200, 'result': 'success!'}
        return json.dumps(res)
    else:
        return json.dumps({'status': 500, 'result': 'check sign fail, code:%d' % check_int})


@server.route('/stock/a_buy_result', methods=['post'])
def stock_a_buy_result():
    """
    查询批量埋单的结果
    :return:
    """
    # 获取通过url请求传参的数据
    # name = request.args.get('name')
    data = json.loads(request.data)
    logger.info("请求体的数据:%s" % data)

    # 校验数据
    check_int = encrypt.check_encrypt(data)
    if check_int == 0:
        # 创建dbf文件
        # logger.info("stock list: %s" % data['data'])
        result_list = dbf_utils.r_a_buy_result_file()
        res = {'status': 200, 'result': 'success!', 'data': result_list}
        return json.dumps(res)
    else:
        return json.dumps({'status': 500, 'result': 'check sign fail, code:%d' % check_int})


@server.route('/stock/a_buy_query/orderid', methods=['post'])
def stock_a_buy_query_by_orderid():
    """
    查询批量埋单的结果
    :return:
    """
    # 获取通过url请求传参的数据
    # name = request.args.get('name')
    data = json.loads(request.data)
    logger.info("请求体的数据:%s" % data)

    # 校验数据
    check_int = encrypt.check_encrypt(data)
    if check_int == 0:
        # 创建dbf文件
        # logger.info("stock list: %s" % data['data'])
        o = dbf_utils.r_a_buy_result_by_orderid(data['orderid'])
        res = {'status': 200, 'result': 'success!', 'data': o}
        return json.dumps(res)
    else:
        return json.dumps({'status': 500, 'result': 'check sign fail, code:%d' % check_int})


if __name__ == '__main__':
    server.run(debug=True, port=base_config.web_port, host=base_config.web_host)