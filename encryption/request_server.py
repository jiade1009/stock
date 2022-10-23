#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : request_server.py
# @Description : 服务端进行签名验签
# @Author      : sam
# @Time        : 2022年 10月 21日 15:25
# @Version     : 1.0
from flask import Flask, request
import json
from flask_cors import CORS
from encryption.sign_utils import get_sign


app = Flask(__name__)
# 允许跨域
CORS(app, resources=r'*')


@app.route('/api', methods=['POST'])
def api():
    data = json.loads(request.data)
    print("请求体的数据:{}".format(data))
    sign = data["sign"]
    del data["sign"]
    # 将请求的数据去除sign之后，用相同的key去加密，得到一个new_sign
    new_sign = get_sign(data, key="hello")
    print("服务端的签名：{}".format(new_sign))
    # 判断客户端发过来的签名是否与服务端的签名一致
    if sign == new_sign:
        '''do something
            、、、
            、、、
        '''
        res = {"status": 200, }
        return json.dumps(res)
    else:
        return json.dumps({"status": 500})


if __name__ == '__main__':
    app.run(host='localhost', port=18022, debug=True)
