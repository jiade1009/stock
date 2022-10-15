#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
根据股票的代码，获取股票的周线行情数据
将数据压缩文件保存在服务器
记录每次下载周线行情数据的操作结果
"""
import numpy as np
import os
import pandas as pd
import datetime
import traceback
import math
import akshare as ak
import libs.common as common
from log.logUtils import logger
import libs.basic_conf as basic_conf
import jobs.stock_weekly_line_ema_job as stock_weekly_line_ema_job

batch_size = 100  # 每100条数据加载一次
# 设置基础目录，每次加载使用。
stock_weekly_dir = basic_conf.cfg_stock_weekly_history_tmp
if not os.path.exists(stock_weekly_dir):
    os.makedirs(stock_weekly_dir)  # 创建多个文件夹结构。
    logger.info("######################### init stock_weekly_dir dir #########################")

# 数据表插入语句
insert_weekly_result = basic_conf.cfg_sql_insert_weekly_result
# 复权方式
rehabilitation_way = "qfq"


def load_weekly_line(date_weekly_research: str, date_weekly_start: str, generate_type: int):
    """
    下载股票的周线数据
    :param date_weekly_research: 周线数据截止日期 yyyyMMdd
    :param date_weekly_start: 周线数据起始日期 yyyyMMdd
    :param generate_type: 生成方式，0手动，1自动
    :return:
    """
    logger.info("load A stock weekly line, date_weekly_research=%s, date_weekly_start=%s" %
                (date_weekly_research, date_weekly_start))
    now_create = datetime.datetime.now()
    sql_count = """ SELECT count(1) FROM  stock_basic_info """
    count = common.select_count(sql_count)
    end = int(math.ceil(float(count) / batch_size) * batch_size)
    result_desc = ""
    for i in range(0, end, batch_size):
        try:
            print("loop :", i)
            sql_1 = """ SELECT * FROM stock_basic_info  limit %s , %s """
            print(sql_1)
            data = pd.read_sql(sql=sql_1, con=common.engine(), params=[i, batch_size])
            if data is not None:
                logger.info("-----开始进行第%d批次的周线历史数据下载-----\n" % (i+1))
                stock_data_df = pd.DataFrame(data, index=data.index.values)
                stock_data_df.apply(get_hist_data_cache, axis=1, date_weekly_research=date_weekly_research,
                                    date_weekly_start=date_weekly_start, result_desc=result_desc)
        except Exception as e:
            result_desc += "=====周线历史数据下载失败：=====\n%s" % e
            logger.error("select sql error :%s %s", e.__class__.__name__, e)
            traceback.print_exc()

    # 保存执行结果
    time_end = datetime.datetime.now()
    result_status = 0 if len(result_desc) == 0 else 1
    sql_params = (rehabilitation_way, date_weekly_research, date_weekly_start, result_status, 0,
                  now_create.strftime("%Y-%m-%d %H:%M:%S"), time_end.strftime("%Y-%m-%d %H:%M:%S"), generate_type,
                  result_desc, "")
    weekly_result_id = common.insert(insert_weekly_result, sql_params)

    # 根据主键id，生成weekly_line_ema
    if weekly_result_id is not None:
        weekly_ema_id = stock_weekly_line_ema_job.save_ema_by_weekly_line_id(weekly_result_id)
        weekly_ema_result = 1
        weekly_ema_result_desc = "ema数据生成"
        if weekly_ema_id == -1:
            weekly_ema_result = 2
            weekly_ema_result_desc = "生成对应的ema数据失败！"
            logger.error("生成对应的ema数据失败！")
        common.insert(basic_conf.cfg_sql_update_weekly_result_by_id,
                      params={weekly_ema_result, weekly_ema_result_desc, weekly_result_id})
    else:
        logger.error("插入 weekly line 数据失败！")


def get_hist_data_cache(item, date_weekly_research, date_weekly_start, result_desc):
    """
    获取周线历史行情数据
    根据周线调研日期和周线起始日期，判断本地文件是否缓存过，如果有，则直接读取，否则的话，ak下载
    :param item:
    :param date_weekly_research:
    :param date_weekly_start:
    :param result_desc:
    :return:
    """
    code = item["code"]
    cache_dir = stock_weekly_dir % (date_weekly_research[0:6], date_weekly_start+"_"+date_weekly_research)
    # 如果没有文件夹创建一个。月文件夹和日文件夹。方便删除。
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_file = cache_dir + "%s_%s^%s.gzip.pickle" % (date_weekly_start, date_weekly_research, code)
    # 如果缓存存在就直接返回缓存数据。压缩方式。
    if os.path.isfile(cache_file):
        logger.info("######### read from cache %s #########" % cache_file)
        return pd.read_pickle(cache_file, compression="gzip")
    else:
        logger.info("####### get data, write cache ####### %s %s %s" % (code, date_weekly_start, date_weekly_research))
        stock_df = ak.stock_zh_a_hist(symbol=code, start_date=date_weekly_start, end_date=date_weekly_research,
                                      adjust=rehabilitation_way, period="weekly")
        if stock_df.empty:
            result_desc += "[%s] 周数据下载失败\n" % code
            return None
        stock_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 'quote_change',
                            'ups_downs', 'turnover']
        stock_df = stock_df.sort_index(axis=0, ascending=False)  # 将数据按照日期排序下。
        # print(stock)
        stock_df.to_pickle(cache_file, compression="gzip")
        return stock_df


logger.info(".........stock_weekly_line_job run .........")
if __name__ == '__main__':
    # 获取周线数据起始日期
    databasetype = common.select(basic_conf.cfg_sql_select_databasetype_by_code, params={"stk_weekly_start_date"})
    # databasetype = pd.read_sql(sql=sql_1, con=common.engine(), params=[i, batch_size])
    stk_weekly_start_date = "20200101"  # 默认起始日期
    if len(databasetype) > 0:
        stk_weekly_start_date = databasetype[0][3]
        print("get from db, stk_weekly_start_date=%s" % stk_weekly_start_date)
    date_weekly_search = datetime.datetime.now().strftime("%Y%m%d")

    # date_weekly_search, stk_weekly_start_date = "20220930", "20220901"
    load_weekly_line(date_weekly_search, stk_weekly_start_date, 1)
