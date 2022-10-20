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
import libs.date_utils as date_utils
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
now_create = datetime.datetime.now()
now_create_str = now_create.strftime("%Y%m%d")
previous_3_dates = []  # 包括周线调研日的在内的前3个周线日
is_trade_date = True  # 调研日是否是交易日
# 处理结果状态和备注
result_status, result_desc = 0, ""


def load_weekly_line(date_weekly_research: str, date_weekly_start: str, generate_type: int):
    """
    下载股票的周线数据
    1.日期判断
      1.1 是否大于当前时间，如果大于，则将调研日调整为当前时间
      1.2 判断调研日是不是交易日，如果调研日不是交易日，则需要将调研日更新为离它最近的一次交易日
    2.分每100支股票批次读取股票周线数据
      2.1 先读取本地是否已经下载过相同交易时段的周线，如果有，直接读取本地数据；如果没有，则开始判断是否存在与其最临近的交易日本地数据
      2.2 如果有临近交易日本地数据，判断调研日同上一交易日是否同一个星期，如果是，说明是同一个周期内的周数据，可以将临近交易日的最后一条数据
      更新最新的周数据。如果不是，说明不是同一个周期内的周数据，则可以直接将最新周数据append到临近交易日本地数据。特别注意：需要比较临近交易
      日同最新下载的数据的前一条周数据是否相同，如果不同，以上逻辑作废，直接重新下载最新的周线（可能存在分红、配股等情况）
    3.保存周线执行结果
    4.根据主键id，生成weekly_line_ema
    :param date_weekly_research: 周线数据截止日期 yyyyMMdd
    :param date_weekly_start: 周线数据起始日期 yyyyMMdd
    :param generate_type: 生成方式，0手动，1自动
    :return:
    """
    global result_status, result_desc, previous_3_dates, batch_size, is_trade_date
    logger.info(".........stock_weekly_line_job run .........")
    # 1.时间判断
    # 1.1 是否大于当前时间，如果大于，则将调研日调整为当前时间
    if date_weekly_research > now_create_str:
        date_weekly_research = now_create_str
    # 获取包括调研日的前3个交易日
    date_weekly_search_str_2 = date_weekly_research[0:4] + "-" + date_weekly_research[4:6] + "-" + \
        date_weekly_research[6:8]
    previous_3_dates = common.select(basic_conf.cfg_sql_select_n_a_trade_date, params=[date_weekly_search_str_2, 3])
    # 1.2 判断调研日是否是交易日，如果不是，则需要将调研日的时间更新为离它最近的一个交易日
    date_tmp = previous_3_dates[0][0]  # 日期格式Y-m-d
    if not date_weekly_research == date_tmp.replace("-", ""):
        is_trade_date = False
        date_weekly_research = date_tmp
    logger.info("load A stock weekly line, date_weekly_research=%s, date_weekly_start=%s" %
                (date_weekly_research, date_weekly_start))

    # 2.分每100支股票批次读取股票周线数据
    sql_count = """ SELECT count(1) FROM  stock_basic_info """
    count = common.select_count(sql_count)
    end = int(math.ceil(float(count) / batch_size) * batch_size)
    # end = 1
    for i in range(0, end, batch_size):
        try:
            sql_1 = """ SELECT * FROM stock_basic_info  limit %s , %s """
            data = pd.read_sql(sql=sql_1, con=common.engine(), params=[i, batch_size])
            # data = pd.read_sql(sql=sql_1, con=common.engine(), params=[14, 1])

            if data is not None:
                logger.info("-----开始进行第%d批次的周线历史数据下载，数量：%s-----\n" % (i+1, len(data)))
                stock_data_df = pd.DataFrame(data['code'], index=data.index.values)
                stock_data_df.apply(get_hist_data_cache_2, axis=1, date_weekly_research=date_weekly_research,
                                    date_weekly_start=date_weekly_start)
        except Exception as e:
            result_desc += "=====第%d批次的周线历史数据下载失败：=====\n%s" % (i+1, e)
            logger.error("开始进行第%d批次周历史数据下载 error :%s %s", i+1, e.__class__.__name__, e)
            traceback.print_exc()

    # 3.保存周线执行结果
    time_end = datetime.datetime.now()
    if len(result_desc) > 0:
        result_status = 1
    sql_params = (rehabilitation_way, date_weekly_research, date_weekly_start, result_status, 0,
                  now_create.strftime("%Y-%m-%d %H:%M:%S"), time_end.strftime("%Y-%m-%d %H:%M:%S"), generate_type,
                  result_desc, "")
    weekly_result_id = common.insert(insert_weekly_result, sql_params)

    # 4.根据主键id，生成weekly_line_ema
    create_weekly_ema(weekly_result_id)


def create_weekly_ema(weekly_result_id):
    """
    根据 周线结果表id，申请计算ema数据
    :param weekly_result_id:
    :return:
    """
    if weekly_result_id is not None:
        weekly_ema_id = stock_weekly_line_ema_job.save_ema_by_weekly_line_id(weekly_result_id)
        weekly_ema_result = 1
        weekly_ema_result_desc = "ema数据生成"
        if weekly_ema_id == -1:
            weekly_ema_result = 2
            weekly_ema_result_desc = "生成对应的ema数据失败！"
            logger.error("生成对应的ema数据失败！")
        common.insert(basic_conf.cfg_sql_update_weekly_result_by_id,
                      params=[weekly_ema_result, weekly_ema_result_desc, weekly_result_id])
    else:
        logger.error("插入 weekly line 数据失败！")


def get_hist_data_cache(item, date_weekly_research, date_weekly_start):
    """
    获取周线历史行情数据
    根据周线调研日期和周线起始日期，判断本地文件是否缓存过，如果有，则直接读取，否则的话，ak下载
    :param item: 对象 ['code'] 股票代码
    :param date_weekly_research: 周线调研日期
    :param date_weekly_start: 周线起始日期
    :return:
    """
    global result_desc
    code = item['code']
    cache_dir = stock_weekly_dir % (date_weekly_research[0:6], date_weekly_start+"_"+date_weekly_research)
    # 如果没有文件夹创建一个，月文件夹和日文件夹
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    cache_file = cache_dir + "%s_%s^%s.gzip.pickle" % (date_weekly_start, date_weekly_research, code)
    # 如果缓存存在就直接返回缓存数据。压缩方式。
    if os.path.isfile(cache_file):
        logger.info("######### read from cache %s #########" % cache_file)
        return pd.read_pickle(cache_file, compression="gzip")
    else:
        return down_a_hist(code, date_weekly_research, date_weekly_start, cache_file)


def down_a_hist(code, date_weekly_research, date_weekly_start, file_path):
    """
    调用ak接口下载指定的周线数据，周线按照日期升序排序
    :param code:
    :param date_weekly_research:
    :param date_weekly_start:
    :param file_path: 保存路径
    :return:
    """
    global result_desc
    logger.info("####### get data, write cache ####### %s %s %s" % (code, date_weekly_start, date_weekly_research))
    stock_weekly_df = ak.stock_zh_a_hist(symbol=code, start_date=date_weekly_start, end_date=date_weekly_research,
                                         adjust=rehabilitation_way, period="weekly")
    if stock_weekly_df.empty:
        result_desc += "[%s] 周数据下载失败\n" % code
        return None
    else:
        stock_weekly_df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                                   'quote_change', 'ups_downs', 'turnover']
        # stock_df = stock_df.sort_index(axis=0, ascending=False)  # 将数据按照日期降序排序下。
        # print(stock)
        stock_weekly_df.to_pickle(file_path, compression="gzip")
        return stock_weekly_df


def get_hist_data_cache_2(item, date_weekly_research, date_weekly_start):
    """
    获取周线历史行情数据
    2.1 先读取本地是否已经下载过相同交易时段的周线，如果有，直接读取本地数据；如果没有，则开始判断是否存在与其最临近的交易日本地数据
    2.2 如果有临近交易日本地数据，判断调研日同上一交易日是否同一个星期，如果是，说明是同一个周期内的周数据，可以将临近交易日的最后一条数据
      更新最新的周数据。如果不是，说明不是同一个周期内的周数据，则可以直接将最新周数据append到临近交易日本地数据。特别注意：需要比较临近交易
      日同最新下载的数据的前一条周数据是否相同，如果不同，以上逻辑作废，直接重新下载最新的周线（可能存在分红、配股等情况）
    :param item: 对象 ['code'] 股票代码
    :param date_weekly_research:
    :param date_weekly_start:
    :return:
    """
    global result_desc, previous_3_dates
    code = item['code']
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
        # 如果不存在，判断是否存在上一个交易日的文件
        previous_1_date = previous_3_dates[1][0]  # 日期格式Y-m-d
        if len(previous_1_date) != 0:
            previous_1_date = previous_1_date.replace("-", "")
            previous_1_dir = stock_weekly_dir % (previous_1_date[0:6], date_weekly_start+"_"+previous_1_date)
            previous_1_file = previous_1_dir + "%s_%s^%s.gzip.pickle" % (date_weekly_start, previous_1_date, code)
            if os.path.isfile(previous_1_file):
                # 存在前一个交易日的文件，开始读取
                previous_1_data = pd.read_pickle(previous_1_file, compression="gzip")
                # 判断是否是同一个周期内的交易日
                in_week = date_utils.in_same_week(previous_1_date, date_weekly_research)
                if in_week:
                    logger.info("在同一个交易周期，则直接将查询到的最新的交易数据替换历史数据的倒数第一条")
                    previous_1_last_but_one = previous_1_data.iloc[[len(previous_1_data)-2]]  # 倒数第二条周线数据
                    last_but_one_date = previous_1_last_but_one["date"].tolist()[0]
                    # 下载最新二个周期的历史行情信息，可能存在异常：如果date_weekly_research正好处在本周交易日，
                    # 且不是当天交易日，那么本周的周线会读取不到，因此判断，如果只有查询到一条数据，那么就不读取本地文件
                    last_2_weekly_df = ak.stock_zh_a_hist(symbol=code, start_date=last_but_one_date.replace("-", ""), end_date=date_weekly_research,
                                              adjust=rehabilitation_way, period="weekly")
                    if len(last_2_weekly_df) == 2:
                        # 比较是否相同
                        same_date = np.array(previous_1_last_but_one).tolist() == np.array(last_2_weekly_df.iloc[[0]]).tolist()
                        if same_date:
                            previous_1_data.iloc[[len(previous_1_data)-1]] = last_2_weekly_df.iloc[[1]]
                            previous_1_data.to_pickle(cache_file, compression="gzip")
                            # 将新数据写入新文件内
                            logger.info("####### 周线数据相同，更新历史数据的最后一条新周线记录 ####### %s %s %s" %
                                        (code, date_weekly_start, date_weekly_research))
                            return previous_1_data
                else:
                    logger.info("不在同一个交易周期，则直接将查询到的最新的交易数据concat到历史数据")
                    previous_1_last_one = previous_1_data.iloc[[len(previous_1_data)-1]]  # 倒数第一条周线数据
                    # 下载最新二个周期的历史行情信息，可能存在异常：如果date_weekly_research正好处在本周交易日，
                    # 且不是当天交易日，那么本周的周线会读取不到，因此判断，如果只有查询到一条数据，那么就不读取本地文件
                    last_2_weekly_df = ak.stock_zh_a_hist(symbol=code, start_date=previous_1_date, end_date=date_weekly_research,
                                                          adjust=rehabilitation_way, period="weekly")
                    if len(last_2_weekly_df) == 2:
                        # 比较是否相同
                        same_date = np.array(previous_1_last_one).tolist() == np.array(last_2_weekly_df.iloc[[0]]).tolist()
                        if same_date:
                            previous_1_data.concat(last_2_weekly_df[[1]], ignore_index=True)
                            previous_1_data.to_pickle(cache_file, compression="gzip")
                            # 将新数据写入新文件内
                            logger.info("####### get previous data from history, write new file ####### %s %s %s" %
                                        (code, date_weekly_start, date_weekly_research))
                            return previous_1_data
        # 未读取到上一个交易日的文件，从ak下载最新的周线数据
        return down_a_hist(code, date_weekly_research, date_weekly_start, cache_file)


if __name__ == '__main__':
    # 获取周线数据起始日期
    databasetype = common.select(basic_conf.cfg_sql_select_databasetype_by_code, params=["stk_weekly_start_date"])
    # databasetype = pd.read_sql(sql=sql_1, con=common.engine(), params=[i, batch_size])
    stk_weekly_start_date = "20200101"  # 默认起始日期
    if len(databasetype) > 0:
        stk_weekly_start_date = databasetype[0][3]
    date_weekly_search = datetime.datetime.now().strftime("%Y%m%d")

    # date_weekly_search, stk_weekly_start_date = "20221016", "20220901"
    load_weekly_line(date_weekly_search, stk_weekly_start_date, 1)
