#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# @Name        : basic_conf.py
# @Description :
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
cfg_mysql_port = "3306"

# ==========stock数据库操作语句==============
# ============ 数据表插入 ==================
# 周线数据导入结果表
cfg_sql_insert_weekly_result = """
INSERT INTO `stock_weekly_line_result` (`rehabilitation_way`, `date_weekly_research`, `date_weekly_start`, 
`result`, `ema_result`, `time_create`, `time_end`, `generate_type`, `result_desc`, `ema_result_desc`)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
# 周线ema数据生成结果表
cfg_sql_insert_weekly_ema_result = """
INSERT INTO `stock_weekly_line_ema_result` (`time_create`, `time_end`, `status`, `status_desc`, `weekly_line_id`, 
`ema_index`) VALUES (%s, %s, %s, %s, %s, %s)
"""
# 股票持有表
cfg_sql_insert_stock_hold = """
INSERT INTO `stock_hold` (`code`, `time_create`, `time_update`, `status`, `buy_amount`, `buy_price`, `hold_amount`, 
`sell_stage`, `weekly_ema_result_id`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
# 股票持有交易记录表
cfg_sql_insert_stock_hold_trade_create = """
INSERT INTO `stock_hold_trade` (`hold_id`, `code`, `amount`, `price`, `trade_type`, `time_create`, `time_update`) 
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


# ============ 数据表查询 ==================
# 根据code进行基础数据信息查询
cfg_sql_select_databasetype_by_code = """
SELECT `id`, `code`, `name`, `value`, `sort_order`, `type` FROM `database_type` WHERE `code`=%s ORDER BY `sort_order` 
"""
# 根据type进行基础数据信息查询
cfg_sql_select_databasetype_by_type = """
SELECT `id`, `code`, `name`, `value`, `sort_order`, `type` FROM `database_type` WHERE `type`=%s ORDER BY `sort_order`
"""
# 根据id查询周线数据结果表
cfg_sql_select_weekly_by_id = """
SELECT * FROM `stock_weekly_line_result` where `id`=%s
"""
# 查询当前正在运行的买入规则
cfg_sql_select_buy_rule_by_status = """
SELECT `id`, `time_market`, `time_market_option`, `rule_period`, `turnover_limit`, `turnover_limit_option`, 
`conver_limit`, `conver_limit_option`, `shock_limit`, `shock_limit_option`, `time_create`, `time_update`, `status` 
FROM `stock_buy_rule` WHERE `status`=%s
"""
# 根据id查询周线ema数据结果和关联的周线结果表
cfg_sql_select_weekly_and_ema = """
SELECT ema.`id` as ema_id, ema.`status` as ema_status, ema.`weekly_line_id`, ema.`ema_index`,  
w.`date_weekly_research`, w.`date_weekly_start`  
FROM `stock_weekly_line_result` w, `stock_weekly_line_ema_result` ema where ema.`id`=%s  
and ema.`weekly_line_id`=w.`id` 
"""
# 根据code查询股票是否在指定上市时间之前上市
cfg_sql_select_stock_before_published = """
SELECT count(*) FROM stock_basic_info WHERE code='%s' and trim(date_publish)<%s 
"""
# 获取包括调研日的前n个的a股交易日，如果调研日不是交易日，那么实际则是在调研日之前的3个交易日
cfg_sql_select_n_a_trade_date = """
SELECT * FROM stock_a_trade_date WHERE trade_date<=%s order by trade_date desc limit %s 
"""
# 查询该股票代码不属于某种状态的数量 (状态，0未购买、1暂停购买、2卖出中、3暂定卖出、4交易结束)
cfg_sql_select_stock_hold_by_code_status = """
SELECT COUNT(*) FROM `stock_hold`  WHERE `code`=%s and `status`<>%s
"""
# 查询属于某种状态的股票 (状态，0未购买、1购买中、2暂停购买、3已购买、4卖出中、5暂定卖出、6交易结束)
cfg_sql_select_stock_hold_by_status = """
SELECT `id`, `code`, `time_create`, `time_update`, `status`, `buy_amount`, `buy_price`, `hold_amount`, 
`sell_stage`, `weekly_ema_result_id` FROM `stock_hold`  WHERE `status`=%s
"""
# 查询当前股票交易的状态
cfg_sql_select_hold_trade_by_id = """
SELECT `id`, `hold_id`, `trade_type`, `orderid`, `status` FROM `stock_hold_trade`  WHERE `id`=%s
"""


# ============ 数据表更新 ==================
# 根据code进行weekly_line_result运行ema生成结果的更新
cfg_sql_update_weekly_result_by_id = """
UPDATE `stock_weekly_line_result` set `ema_result`=%s, `ema_result_desc`=%s where `id`=%s
"""
# 根据id进行weekly_ema_result的运行买入规则的结果更新
cfg_sql_update_weekly_ema_result_by_id = """
UPDATE `stock_weekly_line_ema_result` set `run_status`=%s, `run_status_desc`=%s, `time_run_begin`=%s, 
`time_run_end`=%s where `id`=%s
"""
# 根据id进行stock_hold的状态更新
cfg_sql_update_hold_result_by_id = """
UPDATE `stock_hold` set `status`=%s, `time_update`=%s where `id`=%s
"""
# 根据id进行stock_hold_trade的状态更新
cfg_sql_update_hold_trade_by_id = """
UPDATE `stock_hold_trade` set `orderid`=%s, `message`=%s, `status`=%s, `note`=%s, `taskid`=%s,
 `taskstatus`=%s, `taskmsg`=%s, `taskpro`=%s, `ordernum`=%s, `time_update`=%s where `id`=%s
"""

# ==========stock文件目录设定==============
# 设置日线数据目录
cfg_stock_history_tmp = "/Users/sam/data/stock/cache/hist_daily_cache/%s/%s/"

"""
设置股票历史周线行情数据基础目录 /Users/sam/data/stock/cache/hist_weekly_cache/202209/20200101_20220930/
202209： 周线调研月份，20200101_20220930：周线时间范围
文件内容格式：['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude',
'quote_change', 'ups_downs', 'turnover']
"""
cfg_stock_weekly_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_cache/%s/%s/"

"""
设置股票历史周线收盘价ema行情数据基础目录 /Users/sam/data/stock/cache/hist_weekly_close_ema_cache/18_25_75//202209/20200101_20220930/
18_25_75： 三个ema线， 202209： 周线调研月份，20200101_20220930：周线ema线 时间范围
文件内容格式：date close_18_ema
"""
cfg_stock_weekly_close_ema_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_close_ema_cache/%s/%s/%s/"

"""
设置股票历史周线最高价ema行情数据基础目录 /Users/sam/data/stock/cache/hist_weekly_high_ema_cache/18_25_75//202209/20200101_20220930/
18_25_75： 三个ema线， 202209： 周线调研月份，20200101_20220930：周线ema线 时间范围
文件内容格式：date high_18_ema
"""
cfg_stock_weekly_high_ema_history_tmp = "/Users/sam/data/stock/cache/hist_weekly_high_ema_cache/%s/%s/%s/"



