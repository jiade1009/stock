#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
遍历股票池，筛选出待购买的股票，向qmt纯阳交易客户端发起买入请求，并记录请求信息
"""
import datetime

import libs.basic_conf as basic_conf
import libs.common as common
from libs.db_helper import db_helper
from log.logUtils import logger
from qmtserver import server_request_client


def do_buy_stock():
    """
    1. 选择未购买的股票
    2. 保存买入请求信息
    3. 更新stock_hold中股票的状态
    3. 遍历股票，对每支股票发起买入请求
    :return:
    """
    logger.info(".........do_buy_stock run  .........")
    # 1.先获取买入策略
    # `code`, `time_create`, `time_update`, `status`, `buy_amount`, `buy_price`, `hold_amount`,
    # `sell_stage`, `weekly_ema_result_id`
    un_buy_stocks = db_helper.selectall(basic_conf.cfg_sql_select_stock_hold_by_status, param=["0"])
    # un_buy_stocks2 = common.select(basic_conf.cfg_sql_select_stock_hold_by_status, params=["0"])
    if len(un_buy_stocks) > 0:
        request_list = []
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for item in un_buy_stocks:
            req_stock = {'hold_id': str(item[0]),
                         'code': str(item[1]),
                         'amount': str(item[5]),
                         'price': str(item[6]),
                         }
            # 2.插入股票买入信息
            s_list = [{'sql': basic_conf.cfg_sql_update_hold_result_by_id,
                       'param': ['1', now_str, req_stock['hold_id']]},
                      {'sql': basic_conf.cfg_sql_insert_stock_hold_trade_create,
                       'param': [req_stock['hold_id'], req_stock['code'],
                                 req_stock['amount'], req_stock['price'], 0, now_str, now_str]}]
            id_lists = db_helper.executemany(s_list)
            # 获取新增 stock_hold_trade 的id
            req_stock['hold_trade_id'] = str(id_lists[1])
            request_list.append(req_stock)
        # 3.发起qmt下单请求
        server_request_client.request_buy(request_list)


if __name__ == '__main__':
    do_buy_stock()
