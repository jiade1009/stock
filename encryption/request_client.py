#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : request_client.py
# @Description : 客户端签名，发起请求
# @Author      : sam
# @Time        : 2022年 10月 21日 15:25
# @Version     : 1.0
from encryption.sign_utils import get_sign
import requests, json


if __name__ == "__main__":
    # 加密秘钥
    key = "hello"  # key是双方约定的，我这边就是直接写死一个，与服务端一直
    body = {"username": "alex", "pwd": "123456"}
    sign = get_sign(body, key)
    body["sign"] = sign
    url="http://localhost:18020/api"
    res = requests.post(url=url, data=json.dumps(body))
    print("请求体body={}".format(body))
    print("返回值:{}".format(json.loads(res.content)))