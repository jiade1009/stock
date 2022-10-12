#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : basic_conf.py
# @Description : TODO
"""
定义项目中的使用到的参数，进行统一管理配置
"""
# @Author      : sam
# @Time        : 2022年 10月 10日 17:13
# @Version     : 1.0


# 设置数据库连接
cfg_mysql_host = "127.0.0.1"
cfg_mysql_user = "root"
cfg_mysql_pwd = "mysql0704"
cfg_mysql_db = "vhr"

# 数据表插入
cfg_sql_insert_weekly_result = """
INSERT INTO `stock_weekly_line_result` (`rehabilitation_way`, `date_weekly_research`, `date_weekly_start`, 
`result`, `ema_result`, `time_create`, `time_end`, `generate_type`, `result_desc`, `ema_result_desc`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
# 日线数据
cfg_stock_history_tmp = "/Users/sam/data/stock/cache/hist_daily_cache/%s/%s/"
# 设置股票历史周线行情数据基础目录，每次加载使用。
cfg_stock_weekly_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_cache/%s/%s/"

# 设置股票历史周线ema行情数据基础目录，每次加载使用。
cfg_stock_weekly_ema_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_ema_cache/%s/%s/"

# 设置获取股票代码完整信息（包括行业，上市时间）
cfg_stock_full_basic = 1



