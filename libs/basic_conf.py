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

# ==========设置数据库连接==============
cfg_mysql_host = "127.0.0.1"
cfg_mysql_user = "root"
cfg_mysql_pwd = "mysql0704"
cfg_mysql_db = "vhr"

# ==========stock数据库操作语句==============
# 数据表插入：周线数据导入结果表
cfg_sql_insert_weekly_result = """
INSERT INTO `stock_weekly_line_result` (`rehabilitation_way`, `date_weekly_research`, `date_weekly_start`, 
`result`, `ema_result`, `time_create`, `time_end`, `generate_type`, `result_desc`, `ema_result_desc`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
# 数据表插入：周线ema数据生成结果表
cfg_sql_insert_weekly_ema_result = """
INSERT INTO `stock_weekly_line_ema_result` (`time_create`, `time_end`, `status`, `status_desc`, `weekly_line_id`, `ema_index`)
VALUES (%s, %s, %s, %s, %s, %s)
"""


# 数据表查询：根据code进行基础数据信息查询
cfg_sql_select_databasetype_by_code = """
SELECT `id`, `code`, `name`, `value`, `sort_order`, `type` FROM `database_type` WHERE `code`=%s ORDER BY `sort_order` 
"""
# 数据表查询：根据type进行基础数据信息查询
cfg_sql_select_databasetype_by_type = """
SELECT `id`, `code`, `name`, `value`, `sort_order`, `type` FROM `database_type` WHERE `type`=%s ORDER BY `sort_order`
"""
# 数据表查询：根据id查询周线数据结果表
cfg_sql_select_weekly_by_id = """
SELECT * FROM `stock_weekly_line_result` where `id`=%s
"""

# 数据表更新：根据code进行基础数据信息查询
cfg_sql_update_weekly_result_by_id = """
UPDATE `stock_weekly_line_result` set `ema_result`=%s, `ema_result_desc`=%s where `id`=%s
"""

# ==========stock文件目录设定==============
# 设置日线数据目录
cfg_stock_history_tmp = "/Users/sam/data/stock/cache/hist_daily_cache/%s/%s/"
# 设置股票历史周线行情数据基础目录 /Users/sam/data/stock/cache/hist_weekly_cache/202209/20200101_20220930/
# 202209： 周线调研月份，20200101_20220930：周线时间范围
cfg_stock_weekly_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_cache/%s/%s/"
# 设置股票历史周线ema行情数据基础目录 /Users/sam/data/stock/cache/hist_weekly_cache/18_25_75//202209/20200101_20220930/
# 18_25_75： 三个ema线， 202209： 周线调研月份，20200101_20220930：周线ema线 时间范围
cfg_stock_weekly_ema_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_ema_cache/%s/%s/%s/"




