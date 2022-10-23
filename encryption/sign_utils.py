#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : sign_utils.py
# @Description : TODO
# @Author      : sam
# @Time        : 2022年 10月 21日 15:25
# @Version     : 1.0
import datetime
import hashlib  # 导入模块hashlib
import json


def md5(plaintext: str):
    """
    md5加密算法
    :param plaintext: 需要加密的字符串
    :return: 加密完成的密文
    """
    md = hashlib.md5()  # 创建md5对象
    md.update(plaintext.encode(encoding='utf-8'))
    return md.hexdigest()


def get_sign(params: dict, key: str):
    """
    获取sign签名
    :param params: 接口的请求数据
    :param key: 客户端与服务端约定的key
    :return: 签名
    """
    # 去除json字符串中：与值之间的空格
    print(params)
    result = json.dumps(params, separators=(",", ":"))
    result_new = result + '&key=' + key
    # md5加密，并转为大写。
    sign_text = md5(result_new).upper()
    # 返回sign
    return sign_text


if __name__ == '__main__':
    now_str = datetime.datetime.now().strftime("%Y%m%d")
    body = {"username": "jack", "password": "aaa123456", "ghk_tm": now_str, "ghk_src": "1"}
    sign = get_sign(body, "hello")
    print(sign)
