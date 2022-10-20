#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : date_utils.py
# @Description : 处理时间的工具库
# @Author      : sam
# @Time        : 2022年 10月 18日 16:17
# @Version     : 1.0
import datetime


def in_same_week(date1: str, date2: str) -> bool:
    """
    两个日期是否在同一个星期
    :param date1: 日期字符串，格式%Y%m%d
    :param date2: 日期字符串，格式%Y%m%d
    :return:
    """
    if date1 > date2:
        date1, date2 = date2, date1
    d2 = datetime.datetime.strptime(date2, "%Y%m%d")
    w2 = d2.weekday()
    d2_tmp = (d2 + datetime.timedelta(days=-w2)).strftime("%Y%m%d")
    return True if d2_tmp <= date1 else False


if __name__ == '__main__':
    date_1, date_2 = "20221021", "20221017"
    print(in_same_week(date_1, date_2))
