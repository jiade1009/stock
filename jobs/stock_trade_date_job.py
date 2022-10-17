#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
获取股票交易的日历
数据来源：新浪财经的股票交易日历数据
"""
import akshare as ak

import libs.common as common
from log.logUtils import logger


def load_a_trade_date() -> int:
    """
    下载最新的A股股票交易日历
    :return: 0成功，-1失败
    """
    logger.info("load A stock trade date")
    tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
    print(tool_trade_date_hist_sina_df)
    tool_trade_date_hist_sina_df.set_index("trade_date", inplace=True)

    # 删除老数据
    del_sql = " DELETE FROM `stock_a_trade_date` "
    common.insert(del_sql)

    # 插入新数据
    common.insert_db(tool_trade_date_hist_sina_df, "stock_a_trade_date", True, "`trade_date`")
    return 0


def get_previous_date(trade_date: str, num: int = 1) -> list:
    """
    获取前num个交易日
    :param trade_date:
    :param num:
    :return: 返回list数据，[[trade_date], [trade_date], ..., [trade_date]]
    """
    select_sql = "SELECT * FROM `stock_a_trade_date` WHERE `trade_date`<'%s' order by `trade_date` desc limit %s " % \
                 (trade_date, num)
    result = common.select(select_sql)
    logger.info(result)
    return result


logger.info(".........stock_trade_date_job run .........")
if __name__ == '__main__':
    load_a_trade_date()
    r = get_previous_date('2022-10-17', 3)
