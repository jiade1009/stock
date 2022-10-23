#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
向qmt纯阳交易客户端发起买入结果的查询请求，并记录请求信息
"""
import datetime

import libs.basic_conf as basic_conf
import libs.common as common
from libs.db_helper import db_helper
from log.logUtils import logger
from qmtserver import server_request_client


def do_buy_query():
    """
    1. 向qmt纯阳交易客户端发起买入交易结果查询
    2. 遍历处理返回回来的每条记录，记录的note字段存放的是 hold_trade_id
    3. 根据hold_trade_id 查询获得交易的类型（trade_type），状态（status），判断该交易结果是否已经更新过。如果更新过，则不做任何操作，
    如果为更新，则根据交易类型和状态，确定stock_hold的股票状态
    3. 更新stock_hold中股票的状态、更新hold_trade信息
    """
    logger.info(".........do_buy_query run  .........")
    result = server_request_client.request_buy_result()
    if result['status'] == 200:
        result_data_list = result['data']
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 遍历处理每条记录
        # 0-ORDERID 1-MESSAGE 2-STATUS 3-NOTE  4 - TASKID    5 - TASKSTATUS6 - TASKMSG   7 - TASKPRO   8 - ORDERNUM
        for item in result_data_list:
            note = item[3]
            hold_trade_id = note.strip()
            status = item[2].strip()
            # `id`, `hold_id`, `trade_type`, `orderid`, `status`
            hold_trade = db_helper.selectone(basic_conf.cfg_sql_select_hold_trade_by_id, param=[hold_trade_id])
            logger.info(hold_trade)
            hold_id, trade_type = hold_trade[1], hold_trade[2]
            # 判断状态是否一致 (委托/撤单状态，1结束，0执行中，-1失败)
            if hold_trade[3] is None or not str(hold_trade[4]) == status:
                sql_param = [item[0].strip(), item[1].strip(), status, note,
                             item[4].strip(), item[5].strip(), item[6].strip(), item[7].strip(),
                             item[8].strip(), now_str, hold_trade_id]
                # 更新股票池信息，判断各种状态
                # trade_type交易类型：0买入，1卖出，2买入撤销，3卖出撤销
                # hold_status: 状态，0未购买、1购买中、2暂停购买、3已购买、4卖出中、5暂定卖出、6交易结束
                # qmt status: 委托/撤单状态，1结束，0执行中，-1失败
                if status == '1':
                    if trade_type == 0:
                        hold_status = 3
                    elif trade_type == 1:
                        hold_status = 6
                    elif trade_type == 2:
                        hold_status == 2
                    elif trade_type == 3:
                        hold_status = 5
                elif status == '-1':
                    hold_status = 6
                else:
                    # status == '0'
                    if trade_type == 0:
                        hold_status = 1
                    elif trade_type == 1:
                        hold_status = 4
                    elif trade_type == 2:
                        hold_status == 2
                    elif trade_type == 3:
                        hold_status = 5

                # 更新股票池状态、更新股票交易表记录信息
                db_helper.execute(basic_conf.cfg_sql_update_hold_result_by_id, param=sql_param)
                s_list = [{'sql': basic_conf.cfg_sql_update_hold_result_by_id,
                           'param': [hold_status, now_str, hold_id]},
                          {'sql': basic_conf.cfg_sql_update_hold_trade_by_id,
                           'param': sql_param}]
                db_helper.executemany(s_list)
            else:
                logger.info("hold_trade_id: %s状态一致，不需要重复更新", hold_trade_id)
    else:
        logger.error(" 请求查询qmt纯阳交易客户端交易结果查询失败 %s", result)


if __name__ == '__main__':
    do_buy_query()
