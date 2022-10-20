#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
根据股票的周线行情数据，生成对应的ema数据
1.获取需要生成ema数据的
根据周线行情数据，找到其对应下的目录，遍历目录下的文件，生成对应的ema文件
将数据压缩文件保存在服务器
记录每次生成周线ema数据的操作结果
"""
import os
import pandas as pd
import datetime
import stockstats
import libs.common as common
import libs.fileUtils as fileUtils
from log.logUtils import logger
import libs.basic_conf as basic_conf

batch_size = 1  # 每100条数据加载一次
# 设置基础目录，每次加载使用。
stock_weekly_close_ema_dir = basic_conf.cfg_stock_weekly_close_ema_history_tmp
if not os.path.exists(stock_weekly_close_ema_dir):
    os.makedirs(stock_weekly_close_ema_dir)  # 创建多个文件夹结构。
    logger.info("######################### init stock_weekly_close_ema_dir dir #########################")

stock_weekly_high_ema_dir = basic_conf.cfg_stock_weekly_high_ema_history_tmp
if not os.path.exists(stock_weekly_high_ema_dir):
    os.makedirs(stock_weekly_high_ema_dir)  # 创建多个文件夹结构。
    logger.info("######################### init stock_weekly_high_ema_dir dir #########################")

# 默认三根ema数据线
default_ema_index_values = (18, 25, 75)
# 数据表插入语句
insert_weekly_ema_result = basic_conf.cfg_sql_insert_weekly_ema_result
# 复权方式
rehabilitation_way = "qfq"


def save_ema_by_weekly_line_id(weekly_line_id: int):
    """
    根据id，获取weekly_line
    :param weekly_line_id:
    :return: 操作状态，成功则返回新增的weekly_ema_result_id，失败返回-1
    """
    logger.info(".........stock_weekly_line_ema_job run .........")
    weekly_line_result_bean = common.select(basic_conf.cfg_sql_select_weekly_by_id, params=[weekly_line_id])
    # logger.info(weekly_line_result_bean)
    if len(weekly_line_result_bean) > 0:
        return save_weekly_line_ema(weekly_line_result_bean[0])
    else:
        logger.error("周线数据结果id不存在，请核对后重新操作！")
        return -1


def save_weekly_line_ema(weekly_line_result_bean: dict):
    """
    根据周线数据，生成对应的ema数据
    :param weekly_line_result_bean: 周线数据结果 {`id`, `rehabilitation_way`, `date_weekly_research`, `date_weekly_start`,
    `result`, `ema_result`, `time_create`, `time_end`, `generate_type`, `result_desc`, `ema_result_desc`}
    :return:
    """
    logger.info("save A stock weekly line ema")
    datetime_begin = datetime.datetime.now()
    date_research = weekly_line_result_bean[2]
    date_start = weekly_line_result_bean[3]
    # 获取系统定义的ema指标  `id`, `code`, `name`, `value`, `sort_order`, `type`
    ema_index_list = common.select(basic_conf.cfg_sql_select_databasetype_by_type, params=["stk_ema"])
    if len(ema_index_list) == 3:
        ema_index_values = (ema_index_list[0][3], ema_index_list[1][3], ema_index_list[2][3])
    else:
        logger.error("weekly line ema 指标不完整，需要3条ema数据，请在databaseType中设定类型为stk_ema数据，默认为18，25，75！")
        ema_index_values = default_ema_index_values

    # 根据周线数据结果找到对应的周线存放路径
    weekly_line_dir = basic_conf.cfg_stock_weekly_history_tmp % (date_research[0:6], date_start+"_"+date_research)
    dirs_files = fileUtils.traversal_files(weekly_line_dir)

    ema_join = "_".join(ema_index_values)
    # 周线close_ema数据保存路径
    cache_close_ema_dir = stock_weekly_close_ema_dir % (ema_join, date_research[0:6], date_start+"_"+date_research)
    if not os.path.exists(cache_close_ema_dir):
        os.makedirs(cache_close_ema_dir)
    logger.info("close_ema_保存路径：%s" % cache_close_ema_dir)

    # 周线high_ema数据保存路径
    cache_high_ema_dir = stock_weekly_high_ema_dir % (ema_join, date_research[0:6], date_start+"_"+date_research)
    if not os.path.exists(cache_high_ema_dir):
        os.makedirs(cache_high_ema_dir)
    logger.info("high_ema_保存路径：%s" % cache_high_ema_dir)

    files = dirs_files["files"]
    result_desc = ""
    if len(files) > 0:
        for file in files:
            filename = file.name
            # 隐藏文件不处理
            if not filename.startswith("."):
                # 获取文件完整的文件名和后缀名
                # filename, extension = os.path.splitext(file)
                # 文件名格式：20220901_20220930^000060.gzip.pickle
                stock_code = filename.split(".")[0].split("^")[1]
                logger.info(" load %s stock weekly_line : %s " % (stock_code, file.path))
                weekly_line_df = pd.read_pickle(file.path, compression="gzip")
                # 进行ema数据的生成
                stock_df = stockstats.wrap(weekly_line_df)
                for idx in ema_index_values:
                    close_idx_ema = stock_df.get("close_%s_ema" % idx)  # 格式：date	close_18_ema
                    cache_close_file = cache_close_ema_dir + "close_ema_%s_%s_%s^%s.gzip.pickle" % (idx, date_start,
                                                                                              date_research, stock_code)
                    close_idx_ema.to_pickle(cache_close_file, compression="gzip")
                    logger.info("成功生成 close_ema_%s_%s_%s^%s 数据指标" % (idx, date_start, date_research, stock_code))

                    high_idx_ema = stock_df.get("high_%s_ema" % idx)  # 格式：date	high_18_ema
                    cache_high_file = cache_high_ema_dir + "high_ema_%s_%s_%s^%s.gzip.pickle" % (idx, date_start,
                                                                                                 date_research,
                                                                                                 stock_code)
                    high_idx_ema.to_pickle(cache_high_file, compression="gzip")
                    logger.info("成功生成 high_ema_%s_%s_%s^%s 数据指标" % (idx, date_start, date_research, stock_code))
    # 开始保存ema生成结果信息
    datetime_end = datetime.datetime.now()
    result_status = 0 if len(result_desc) == 0 else -1

    sql_params = (datetime_begin.strftime("%Y-%m-%d %H:%M:%S"), datetime_end.strftime("%Y-%m-%d %H:%M:%S"),
                  result_status, result_desc, weekly_line_result_bean[0], ema_join)
    weekly_ema_result_id = common.insert(insert_weekly_ema_result, sql_params)
    return weekly_ema_result_id


if __name__ == '__main__':
    save_ema_by_weekly_line_id(weekly_line_id=7)
