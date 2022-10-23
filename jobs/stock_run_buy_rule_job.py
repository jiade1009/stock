#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
根据买入规则，ema文件数据，计算出满足条件的股票代码
记录每次计算的操作结果
"""
import datetime

import pandas as pd

import libs.basic_conf as basic_conf
import libs.common as common
import libs.fileUtils as fileUtils
from log.logUtils import logger

# 今天的时间
now = datetime.datetime.now()
now_int = int(now.strftime("%Y%m%d"))
time_run_begin = now.strftime("%Y-%m-%d %H:%M:%S")


def run_buy_rule(weekly_line_ema_result_id: int):
    """
    1. 选择正在运行中的买入策略
    2. 根据传递的ema_result_id 获取对应的周线和ema数据
    3. 根据ema数据，找到对应的weekly的数据文件保存路径，遍历该路径下的文件，读取对应的文件名获取对应的股票代码
    4. 遍历处理股票代码，读取股票代码的close_ema、high_ema数据文件
    5. 根据买入策略，判断每支股票是否满足条件，筛选出合适的股票
      5.1 上市时长判断
      5.2判断在过去的rule_period周之内 close<=ema75
      5.3 判断在过去的rule_period周之内 ema75>=ema18
      5.4 寻找转折点信号：ema18_p<=ema25_p and ema18_t>ema25_t ema18开始突破ema25
      5.5 成交量额度：买入量*20<过去5天的平均成交量。 ？ 暂时未处理
      5.6 收敛度：当天最高价_EMA75/当前最高价_EMA18<conver_limit
      5.7 下跌幅度：最低价/最高价<=shock_limit。
    6. 保存买入股票信息

    :param weekly_line_ema_result_id:
    :return:
    """
    logger.info(".........stock_buy_job run with ema_result_id: %s ........." % weekly_line_ema_result_id)
    # 1.先获取买入策略
    buyRule = common.select(basic_conf.cfg_sql_select_buy_rule_by_status, params=["1"])
    """buyRule.columns = ['id', 'time_market', 'time_market_option', 'rule_period', 'turnover_limit',
                       'turnover_limit_option', 'conver_limit', 'conver_limit_option', 'shock_limit',
                       'shock_limit_option', 'time_create', 'time_update', 'status']
    """
    if len(buyRule) == 0:
        logger.error("当前没有正在运行的买入策略，请先设定买入策略！")
        return -1
    else:
        buyRule = buyRule[0]
        logger.info("当前选择运行的买入策略ID=%s " % str(buyRule[0]))
    rule_period = int(buyRule[3])  # 策略周期

    # 2.获取周线生成结果表
    """['ema_id', 'ema_status', 'weekly_line_id', 'ema_index',
     'date_weekly_research', 'date_weekly_start']"""
    weekly_and_ema_result_bean = common.select(basic_conf.cfg_sql_select_weekly_and_ema,
                                               params=[weekly_line_ema_result_id])
    if len(weekly_and_ema_result_bean) == 0:
        logger.error("周线ema数据结果id不存在，请核对后重新操作！")
        return -2
    else:
        weekly_and_ema_result_bean = weekly_and_ema_result_bean[0]
        logger.info("当前选择周线ema数据结果表ID=%s" % weekly_line_ema_result_id)

    # 3.根据周线和周线ema结果表，找到对应的ema数据文件
    # 周线ema数据保存路径
    ema_index = weekly_and_ema_result_bean[3]
    date_research = weekly_and_ema_result_bean[4]
    date_start = weekly_and_ema_result_bean[5]

    weekly_close_ema_dir = basic_conf.cfg_stock_weekly_close_ema_history_tmp % (ema_index, date_research[0:6],
                                                                                date_start+"_"+date_research)
    weekly_high_ema_dir = basic_conf.cfg_stock_weekly_high_ema_history_tmp % (ema_index, date_research[0:6],
                                                                              date_start+"_"+date_research)
    ema_index_list = ema_index.split("_")  # 对应的三根 ema线
    logger.info(ema_index_list)
    # 周线结果保存路径
    weekly_line_dir = basic_conf.cfg_stock_weekly_history_tmp % (date_research[0:6], date_start+"_"+date_research)
    dirs_files = fileUtils.traversal_files(weekly_line_dir)
    # 4.遍历获取文件下的所有股票代码
    files = dirs_files["files"]
    white_stock_list = []  # 存放满足白色信号线的股票ema18突破ema25
    buy_stock_list = []  # 存放满足买入规则的股票
    if len(files) > 0:
        for file in files:
            filename = file.name
            # 隐藏文件不处理
            if not filename.startswith("."):
                # 获取文件完整的文件名和后缀名
                # filename, extension = os.path.splitext(file)
                # 文件名格式：20220901_20220930^000060.gzip.pickle
                stock_code = filename.split(".")[0].split("^")[1]
                logger.info(" read %s stock weekly_line filename: %s " % (stock_code, filename))
                # 进行周线数据的读取
                weekly_line = pd.read_pickle(file, compression="gzip")
                weekly_line.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
                                       'quote_change', 'ups_downs', 'turnover']
                weekly_line.set_index('date', inplace=True)  # 设定日期为行索引，日期不做为列数据，所对应的列的序号，均前移一个
                # 进行三条close_ema数据的读取 文件名：close_ema_18_20200101_20221013^000001.gzip.pickle
                close_ema_filepath_0 = \
                    weekly_close_ema_dir + "close_ema_%s_%s_%s^%s.gzip.pickle" % \
                    (ema_index_list[0], date_start, date_research, stock_code)
                close_ema_0 = pd.read_pickle(close_ema_filepath_0, compression="gzip")  # 文件内容格式：date	close_18_ema

                close_ema_filepath_1 = \
                    weekly_close_ema_dir + "close_ema_%s_%s_%s^%s.gzip.pickle" % \
                    (ema_index_list[1], date_start, date_research, stock_code)
                close_ema_1 = pd.read_pickle(close_ema_filepath_1, compression="gzip")

                close_ema_filepath_2 = \
                    weekly_close_ema_dir + "close_ema_%s_%s_%s^%s.gzip.pickle" % \
                    (ema_index_list[2], date_start, date_research, stock_code)
                close_ema_2 = pd.read_pickle(close_ema_filepath_2, compression="gzip")

                # 进行三条high_ema数据的读取 文件名：high_ema_18_20200101_20221013^000001.gzip.pickle
                high_ema_filepath_0 = \
                    weekly_high_ema_dir + "high_ema_%s_%s_%s^%s.gzip.pickle" % \
                    (ema_index_list[0], date_start, date_research, stock_code)
                high_ema_0 = pd.read_pickle(high_ema_filepath_0, compression="gzip")  # 文件内容格式：date	high_18_ema

                high_ema_filepath_1 = \
                    weekly_high_ema_dir + "high_ema_%s_%s_%s^%s.gzip.pickle" % \
                    (ema_index_list[1], date_start, date_research, stock_code)
                high_ema_1 = pd.read_pickle(high_ema_filepath_1, compression="gzip")

                high_ema_filepath_2 = \
                    weekly_high_ema_dir + "high_ema_%s_%s_%s^%s.gzip.pickle" % \
                    (ema_index_list[2], date_start, date_research, stock_code)
                high_ema_2 = pd.read_pickle(high_ema_filepath_2, compression="gzip")

                # 根据买入规则进行股票分析
                if buyRule[2] == 1:  # 5.1上市时长判断
                    judge_date_int = now_int - int(buyRule[1])*10000
                    count_sql = basic_conf.cfg_sql_select_stock_before_published % (stock_code, judge_date_int)
                    stock_before_year = common.select_count(count_sql)
                    if stock_before_year == 0:  # 没有满足条件
                        logger.warning(" 股票code=%s 不满足 上市时间 " % stock_code)
                        continue

                # 特别需要注意，周线、周线EMA中的数据，都是按照时间进行升序排序的，因此在判断ema数据的大小关系，并非从下标0开始
                index_end = len(weekly_line)
                index_begin = (index_end - rule_period) if index_end - rule_period > 0 else 0
                logger.info(" between: %s ~ %s" % (index_begin, index_end))
                # 5.2.判断在过去的rule_period周之内 close<=ema75
                # logger.info(" weekly_line: %s" % weekly_line.iloc[index_begin:index_end, 1])
                # logger.info(" close_ema_2: %s" % close_ema_2.iloc[index_begin:index_end])
                if not (weekly_line.iloc[index_begin:index_end, 1] <= close_ema_2.iloc[index_begin:index_end]).all():
                    logger.warning(" 股票code=%s 不满足 close<=ema75 " % stock_code)
                    continue
                else:
                    logger.info(" =============== 股票code=%s 满足 close<=ema75 " % stock_code)

                # 5.3.判断在过去的rule_period周之内 ema75>=ema18
                # logger.info(" close_ema_0: %s" % close_ema_0.iloc[index_begin:index_end])
                # logger.info(" close_ema_2: %s" % close_ema_2.iloc[index_begin:index_end])
                if not (close_ema_0.iloc[index_begin:index_end] <= close_ema_2.iloc[index_begin:index_end]).all():
                    logger.warning(" 股票code=%s 不满足 ema75>=ema18 " % stock_code)
                    continue
                else:
                    logger.info(" =============== 股票code=%s 满足 ema75>=ema18 " % stock_code)

                # 5.4.寻找转折点信号：ema18_p<=ema25_p and ema18_t>ema25_t ema18开始突破ema25
                # logger.info(" close_ema_0[index_end-2]: %s" % close_ema_0[index_end-2])
                # logger.info(" close_ema_1[index_end-2]: %s" % close_ema_1[index_end-2])
                # logger.info(" close_ema_0[index_end-1]: %s" % close_ema_0[index_end-1])
                # logger.info(" close_ema_1[index_end-1]: %s" % close_ema_1[index_end-1])
                if not (close_ema_0[index_end-2] <= close_ema_1[index_end-2] and
                        close_ema_0[index_end-1] > close_ema_1[index_end-1]):
                    logger.warning(" 股票code=%s 不满足 ema18_p<=ema25_p and ema18_t>ema25_p " % stock_code)
                    continue
                else:
                    logger.info(" =============== 股票code=%s 满足 ema18_p<=ema25_p and ema18_t>ema25_p " % stock_code)
                    white_stock_list.append(stock_code)

                # 5.5.成交量额度：买入量*20<过去5天的平均成交量。 ？ 暂时未处理

                # 5.6.收敛度：当天最高价_EMA75/当前最高价_EMA18<conver_limit
                if buyRule[7] == 1:  # 收敛度判断
                    high_ema_2_0 = high_ema_2[index_end-1]  # 当前的ema75的最高价格
                    high_ema_0_0 = high_ema_0[index_end-1]  # 当前的ema18的最高价格
                    # logger.info(" high_ema_0_0: %s" % high_ema_0_0)
                    # logger.info(" high_ema_2_0: %s" % high_ema_2_0)
                    if not (float(high_ema_2_0)/float(high_ema_0_0) < buyRule[6]):
                        logger.warning(" 股票code=%s 不满足 当天最高价_EMA75/当前最高价_EMA18<conver_limit " % stock_code)
                        continue
                    else:
                        logger.info(" =============== 股票code=%s 满足 收敛度 " % stock_code)

                # 5.7.下跌幅度：最低价/最高价<=shock_limit。
                # 最高价：往前倒推，找到EMA18与EMA75的交叉点，然后往前倒推10周，找出最高价
                if buyRule[9] == 1:
                    i = index_begin
                    # 当跳出while循环，说明找到交叉点（ema18穿过ema75）
                    while not (float(close_ema_0[i-1]) <= float(close_ema_2[i-1]) and float(close_ema_0[i])
                               > float(close_ema_2[i]) or i >= 0):
                        i -= 1
                    # 交叉点往前倒推10周，设定为i的新值，即判断范围为0:i
                    i = i-10 if i-10 >= 0 else 0
                    close_ema_2_max = close_ema_2.iloc[i:index_end].max(axis=0)  # 找到ema_75的最大值
                    close_ema_0_min = close_ema_0.iloc[i:index_end].min(axis=0)  # 找到ema_18的最小值
                    if not (float(close_ema_0_min)/float(close_ema_2_max) <= buyRule[8]):
                        logger.warning(" 股票code=%s 不满足 最低价/最高价<=shock_limit " % stock_code)
                        continue
                    else:
                        logger.info(" =============== 股票code=%s 满足 下跌幅度 " % stock_code)

                # 到达该处，说明找到满足所有的买入规则的股票，记录该信息
                logger.info(" 股票code=%s 满足 买入规则ID=%s " % (stock_code, buyRule[0]))
                buy_stock_list.append(stock_code)

    run_result_code = 0
    run_status_desc = "没有筛选出合适的股票"
    if len(white_stock_list) > 0:
        run_status_desc = "ema18突破ema25股票：【" + ", ".join(white_stock_list)
        run_status_desc += "】。"
        run_result_code = 1
    if len(buy_stock_list) > 0:
        run_status_desc += "满足购买策略股票：【" + ", ".join(buy_stock_list)
        run_status_desc += "】。"

    # sql_params = (datetime_begin.strftime("%Y-%m-%d %H:%M:%S"), datetime_end.strftime("%Y-%m-%d %H:%M:%S"),
    #                   result_status, result_desc, weekly_line_result_bean[0], ema_join)
    # 更新ema_result表数据
    time_run_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    common.insert(basic_conf.cfg_sql_update_weekly_ema_result_by_id,
                  params=["1", run_status_desc, time_run_begin, time_run_end, weekly_line_ema_result_id])
    # 开始保存股票待购买信息
    for code in buy_stock_list:
        # 需要考虑股票池中该股票代码是否存在交易未结束的记录 （股票状态，0未购买、1暂停购买、2卖出中、3暂定卖出、4交易结束）
        exist_sql = basic_conf.cfg_sql_select_stock_hold_by_code_status
        count = common.select_count(exist_sql, params=[code, '4'])
        logger.info("count:%s" % count)
        if count == 0:
            common.insert(basic_conf.cfg_sql_insert_stock_hold, params=[code, time_run_end, time_run_end, 0, 0, 0, 0, 0,
                                                                        weekly_line_ema_result_id])
    return run_result_code


if __name__ == '__main__':
    run_buy_rule(weekly_line_ema_result_id=46)

