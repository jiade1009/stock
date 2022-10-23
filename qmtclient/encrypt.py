#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : encrypt.py
# @Description : 参数的数字签名和验签
# @Author      : sam
# @Time        : 2022年 10月 21日 21:46
# @Version     : 1.0
import datetime

from encryption import sign_utils
from qmtclient import base_config
from qmtclient.logUtils import logger


def do_encrypt(params) -> dict:
    """
    签名
    :param params:
    :return:
    """
    now_int = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    params['tm'] = now_int
    params['idx'] = base_config.encrypt_idx
    sign = sign_utils.get_sign(params, base_config.encrypt_key)
    params['sign'] = sign
    return params


def check_encrypt(data) -> int:
    """
    签名验签，并判断是否在有效的时间内的请求
    需要传递sign、idx、tm三个参数，才能满足
    :param data:
    :return:
    """
    # 1.参数必要性确认
    data_keys = data.keys()
    if 'sign' not in data_keys or 'idx' not in data_keys or 'tm' not in data_keys:
        logger.error("缺少必要的参数：sign、idx、tm！")
        return -2
    sign_text = data['sign']
    encrypt_idx = data['idx']
    tm_text = data['tm']
    # 2.校验时间戳
    now_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    interval = int(now_str) - int(tm_text)
    if interval > base_config.encrypt_interval:
        logger.error("请求参数已经超时！")
        return -3
    # 3.校验数据
    del data['sign']
    new_sign = sign_utils.get_sign(data, base_config.encrypt_key)
    if sign_text == new_sign:
        return 0
    else:
        return -1
