#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

"""
通过获取A股中所有股票的实时行情，整理出当前A股的股票代码
"""
import numpy as np
import pandas as pd
import datetime
import traceback
import akshare as ak
import libs.common as common
from log.logUtils import logger


def stock_a(code) -> bool:
    """
    股票代码判断，判断是否为A股
    沪市主板股票代码：600、601、603、605开头
    深市主板股票代码：000开头
    深市中小板股票代码：002开头
    创业板股票代码：300开头
    科创板股票代码：688开头

    :param code: 股票代码
    :return: bool
    """
    # print(code)
    # print(type(code))
    # 上证A股  # 深证A股
    if code.startswith('600') or code.startswith('601') or code.startswith('603') or code.startswith('605') \
            or code.startswith('000') or code.startswith('002') or code.startswith('300') or code.startswith('688'):
        return True
    else:
        return False


def stock_a_filter_st(name) -> bool:
    """
    判断是否为ST股，过滤掉 st 股票
    :param name: 骨片简称
    :return:
    """
    if name.find("ST") == -1:
        return True
    else:
        return False


def stock_a_filter_price(latest_price) -> bool:
    """
    过滤价格，如果没有基本上是退市了
    float 在 pandas 里面判断 空
    :param latest_price:
    :return:
    """
    if np.isnan(latest_price):
        return False
    else:
        return True


def load_a_stock():
    """
    更新A股股票信息
    1.获取当前A股的行情信息：上证、深证、北证
    2.过滤不符合条件的A股股票
    3.表清空
    4.插入新的数据集合
    :return:
    """
    logger.info("load A stock")
    datetime_int = (datetime.datetime.now()).strftime("%Y%m%d")
    try:
        # 上证_A股 ['证券代码', '证券简称', '扩位证券简称', '上市日期']
        stock_info_sh_A_name_code_df = ak.stock_info_sh_name_code(indicator="主板A股")
        # print("stock_info_sh_A_name_code_df: %s %d" % (stock_info_sh_A_name_code_df.columns,
        #                                                len(stock_info_sh_A_name_code_df)))
        stock_info_sh_A_name_code_df = stock_info_sh_A_name_code_df.drop(columns=['扩位证券简称'])
        stock_info_sh_A_name_code_df.columns = ['code', 'name', 'date_publish']
        # print(stock_info_sh_A_name_code_df.head())

        # 上证_科创 ['证券代码', '证券简称', '扩位证券简称', '上市日期']
        stock_info_sh_KC_name_code_df = ak.stock_info_sh_name_code(indicator="科创板")
        # print("stock_info_sh_KC_name_code_df: %s %d" % (stock_info_sh_KC_name_code_df.columns,
        #                                                 len(stock_info_sh_KC_name_code_df)))
        stock_info_sh_KC_name_code_df = stock_info_sh_KC_name_code_df.drop(columns=['扩位证券简称'])
        stock_info_sh_KC_name_code_df.columns = ['code', 'name', 'date_publish']
        # print(stock_info_sh_KC_name_code_df.head())

        # 深证 ['板块', 'A股代码', 'A股简称', 'A股上市日期', 'A股总股本', 'A股流通股本', '所属行业']
        stock_info_sz_A_name_code_df = ak.stock_info_sz_name_code(indicator="A股列表")
        # print("stock_info_sz_A_name_code_df: %s %d" % (stock_info_sz_A_name_code_df.columns,
        #                                                len(stock_info_sz_A_name_code_df)))
        stock_info_sz_A_name_code_df = stock_info_sz_A_name_code_df.drop(columns=['板块', 'A股总股本', 'A股流通股本', '所属行业'])
        stock_info_sz_A_name_code_df.columns = ['code', 'name', 'date_publish']
        # print(stock_info_sz_A_name_code_df.head())

        # 北证 ['证券代码', '证券简称', '总股本', '流通股本', '上市日期', '所属行业', '地区', '报告日期']
        stock_info_bj_name_code_df = ak.stock_info_bj_name_code()
        # print("stock_info_bj_name_code_df: %s %d" % (stock_info_bj_name_code_df.columns,
        #                                              len(stock_info_bj_name_code_df)))
        stock_info_bj_name_code_df = stock_info_bj_name_code_df.drop(columns=['总股本', '流通股本', '所属行业', '地区', '报告日期'])
        stock_info_bj_name_code_df.columns = ['code', 'name', 'date_publish']
        # print(stock_info_bj_name_code_df.head())

        stock_concat_df = pd.concat([stock_info_sh_A_name_code_df, stock_info_sh_KC_name_code_df,
                                     stock_info_sz_A_name_code_df, stock_info_bj_name_code_df], ignore_index=True)
        # print("stock_concat_df: %s %d" % (stock_concat_df.columns, len(stock_concat_df)))
        # 移除ST股票
        stock_concat_df = stock_concat_df.loc[stock_concat_df["name"].apply(stock_a_filter_st)]
        stock_concat_df['date_publish'] = stock_concat_df['date_publish'].apply(lambda x: str(x).replace("-", ""))
        # print(stock_concat_df.head())

        # 删除老数据
        del_sql = " DELETE FROM `stock_basic_info` "
        common.insert(del_sql)
        stock_concat_df.set_index('code', inplace=True)
        # stock_concat_df.drop('index', axis=1, inplace=True)

        #插入新数据
        common.insert_db(stock_concat_df, "stock_basic_info", True, "`code`")
    except Exception as e:
        logger.error('错误明细是：%s %s', e.__class__.__name__, e)
        traceback.print_exc()

"""
main函数入口
3种传递参数格式：
1. python xxx.py 2017-07-01 10：指定要调用的日期，以及递归循环调用前10日的数据 
2. python xxx.py 2017-07-01：调用指定的日期
3. python xxx.py ：调用当天的日期
"""
if __name__ == '__main__':
    # 执行数据初始化。
    # 使用方法传递。
    print("------------load stock_basic_info run ---------------")
    load_a_stock()

print("............... run .........")
