#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : main.py
# @Description : 服务端的REST API
# @Author      : sam
# @Time        : 2022年 10月 21日 12:32
# @Version     : 1.0
import datetime

import flask
import json

from qmtserver import base_config
from qmtserver.logUtils import logger
from flask import request
from qmtserver import encrypt

'''
flask： web框架，通过flask提供的装饰器@server.route()将普通函数转换为服务
登录接口，需要传url、username、passwd
'''
# 创建一个服务，把当前这个python文件当做一个服务
server = flask.Flask(__name__)


@server.route('/stock/buyresult', methods=['post'])
def stock_buy():
    # 获取通过url请求传参的数据
    # name = request.args.get('name')
    data = json.loads(request.data)
    logger.info("请求体的数据:%s" % data)

    # 校验数据
    check_int = encrypt.check_encrypt(data)
    if check_int == 0:
        res = {'status': 200, 'result': 'success!'}
        return json.dumps(res)
    else:
        return json.dumps({'status': 500, 'result': 'check sign fail, code:%d' % check_int})


if __name__ == '__main__':
    server.run(debug=True, port=base_config.web_port, host=base_config.web_host)
