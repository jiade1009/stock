#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


"""
通过获取A股中所有股票的实时行情，整理出当前A股的股票代码
"""
import libs.common as common
import numpy as np
import akshare as ak
from log.logUtils import logger


def stock_a(code) -> bool:
    """
    股票代码判断，判断是否为A股
    沪市主板股票代码：600、601、603、605开头
    深市主板股票代码：000开头
    深市中小板股票代码：002开头
    创业板股票代码：300开头
    科创板股票代码：688开头

    :param code: 股票代码
    :return: bool
    """
    # print(code)
    # print(type(code))
    # 上证A股  # 深证A股
    if code.startswith('600') or code.startswith('601') or code.startswith('603') or code.startswith('605') \
            or code.startswith('000') or code.startswith('002') or code.startswith('300') or code.startswith('688'):
        return True
    else:
        return False


def stock_a_filter_st(name) -> bool:
    """
    判断是否为ST股，过滤掉 st 股票
    :param name: 骨片简称
    :return:
    """
    if name.find("ST") == -1:
        return True
    else:
        return False


def stock_a_filter_price(latest_price) -> bool:
    """
    过滤价格，如果没有基本上是退市了
    float 在 pandas 里面判断 空
    :param latest_price:
    :return:
    """
    if np.isnan(latest_price):
        return False
    else:
        return True


def load_a_stock(tmp_datetime):
    """
    更新A股股票信息
    1.获取当前A股的行情信息
    2.过滤不符合条件的A股股票
    :param tmp_datetime:
    :return:
    """
    datetime_str = tmp_datetime.strftime("%Y-%m-%d")
    datetime_int = tmp_datetime.strftime("%Y%m%d")
    logger.info("load A stock, date: %s", str(datetime_int))

    try:
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        # columns内容：['序号', '代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '振幅', '最高', '最低',
        #        '今开', '昨收', '量比', '换手率', '市盈率-动态', '市净率', '总市值', '流通市值', '涨速', '5分钟涨跌',
        #        '60日涨跌幅', '年初至今涨跌幅']
        stock_zh_a_spot_em_df.columns = ['index', 'code', 'name', 'latest_price', 'quote_change', 'ups_downs', 'volume',
                                         'turnover', 'amplitude', 'high', 'low', 'open', 'closed', 'quantity_ratio',
                                         'turnover_rate', 'pe_dynamic', 'pb', 'total_market', 'circulate_market',
                                         'growth-rate', 'five_minute', 'sixty-up_down', 'to_date_up_down']

        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.loc[stock_zh_a_spot_em_df["code"].apply(stock_a)]. \
            loc[stock_zh_a_spot_em_df["name"].apply(stock_a_filter_st)]. \
            loc[stock_zh_a_spot_em_df["latest_price"].apply(stock_a_filter_price)]
        # 保留指定的列
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[['code', 'name', 'total_market', 'circulate_market']]
        stock_zh_a_spot_em_df['date'] = datetime_int  # 修改时间成为int类型。

        # 删除老数据。
        del_sql = " DELETE FROM `stock_basic_info` "
        common.insert(del_sql)
        stock_zh_a_spot_em_df.set_index('code', inplace=True)
        # stock_zh_a_spot_em_df.drop('index', axis=1, inplace=True)
        print(stock_zh_a_spot_em_df.head(5))
        common.insert_db(stock_zh_a_spot_em_df, "stock_basic_info", True, "`date`,`code`")
    except Exception as e:
        logger.error('错误明细是：%s %s', e.__class__.__name__, e)


# main函数入口
# 3种传递参数格式：
#
"""
main函数入口
3种传递参数格式：
1. python xxx.py 2017-07-01 10：指定要调用的日期，以及递归循环调用前10日的数据 
2. python xxx.py 2017-07-01：调用指定的日期
3. python xxx.py ：调用当天的日期
"""
if __name__ == '__main__':
    # 执行数据初始化。
    # 使用方法传递。
    print("------------load stock_basic_info run ---------------")
    dt = common.run_with_args(load_a_stock)

print("............... run .........")
