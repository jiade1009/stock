#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : request_utils.py
# @Description : TODO
# @Author      : sam
# @Time        : 2022年 10月 21日 12:34
# @Version     : 1.0

import requests
import json
import datetime
from qmtclient import encrypt


url = '推送数据的目标网址'
headers = {'content-type': "application/json", 'Authorization': 'APP appid = 4abf1a,token = 9480295ab2e2eddb8'}#数据头
body = {"Data": "需要推送的数据", "Time": str(datetime.datetime.now())}
response = requests.post(url, data = json.dumps(body), headers = headers)
print(response.text, response.status_code)