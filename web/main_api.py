"""终端执行某个文件的时候都是直接运行指定文件的，缺少需要检索的路径，需要将我们自定义的模块路径引入"""
# 调用os，sys模块
import os
import sys
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath或者os.path.dirname(__file__)))
# BASE_DIR2 = os.path.abspath(os.path.join(os.getcwd(), ".."))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
# sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9")
# sys.path.append("/Users/sam/Library/Python/3.9/lib/python/site-packages")
# sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
import datetime
from log.logUtils import logger
import libs.common as common
import libs.basic_conf as basic_conf
import jobs.stock_basic_info_job as stock_basic_info_job
import jobs.stock_weekly_line_job as stock_weekly_line_job
import jobs.stock_weekly_line_ema_job as stock_weekly_line_ema_job
import jobs.stock_run_buy_rule_job as stock_buy_job


if __name__ == '__main__':
    logger.info("it is in main_api...")
    argv = sys.argv
    if len(argv) > 1:
        flag = argv[1]
        logger.info("%s is invoked", flag)
        if flag == "load_a_stock":
            stock_basic_info_job.load_a_stock()
        elif flag == "create_a_weekly":
            if len(argv) == 2:
                # 获取周线数据起始日期
                databasetype = common.select(basic_conf.cfg_sql_select_databasetype_by_code,
                                             params=["stk_weekly_start_date"])
                stk_weekly_start_date = "20200101"  # 默认起始日期
                if len(databasetype) > 0:
                    stk_weekly_start_date = databasetype[0][3]
                date_weekly_search = datetime.datetime.now().strftime("%Y%m%d")
                stock_weekly_line_job.load_weekly_line(date_weekly_search, stk_weekly_start_date, 0)
            else:
                logger.error("invoke load_a_weekly_line by 2 params (load_a_weekly_line)")
        elif flag == "create_a_ema":
            if len(argv) == 3:
                stock_weekly_line_ema_job.save_ema_by_weekly_line_id(argv[2])
            else:
                logger.error("invoke stock_weekly_line_ema_job by 2 params (create_a_ema, weekly_result_id)")
        elif flag == "run_a_buy_rule":
            if len(argv) == 3:
                stock_buy_job.run_buy_rule(argv[2])
            else:
                logger.error("invoke stock_buy_job by 2 params (run_a_buy_rule, ema_result_id)")
    else:
        logger.error(" missing parameter")
