"""终端执行某个文件的时候都是直接运行指定文件的，缺少需要检索的路径，需要将我们自定义的模块路径引入"""
# 调用os，sys模块
import os
import sys
import datetime
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath或者os.path.dirname(__file__)))
# BASE_DIR2 = os.path.abspath(os.path.join(os.getcwd(), ".."))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASE_DIR)
# sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9")
# sys.path.append("/Users/sam/Library/Python/3.9/lib/python/site-packages")
# sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")

from log.logUtils import logger
import jobs.stock_basic_info_job as stock_basic_info_job
import jobs.stock_weekly_line_job as stock_weekly_line_job

print("=============")
# if __name__ == '__main__':
#     print("it is in main...")
#
if __name__ == '__main__':
    logger.info("it is in main_api...")
    argv = sys.argv
    if len(argv) > 1:
        flag = argv[1]
        logger.info("%s is invoked", flag)
        if flag == "load_a_stock":
            stock_basic_info_job.load_a_stock()
        elif flag == "load_a_weekly_line":
            if len(argv) == 4:
                stock_weekly_line_job.load_weekly_line(argv[2], argv[3], 0)
            else:
                logger.error("invoke load_a_weekly_line by 3 params (load_a_weekly_line, date_search, date_start)")
    else:
        logger.error(" missing parameter")
