#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
# @Name        : pickle2csv.py
# @Description : 将gzip.pickle文件导出转成csv文件
# @Author      : sam
# @Time        : 2022年 10月 13日 11:40
# @Version     : 1.0


def pickle2csv(src: str, dest: str):
    file_pd = pd.read_pickle(src, compression="gzip")
    file_pd.to_excel(dest)


if __name__ == '__main__':
    src0 = "/Users/sam/data/stock/cache/hist_weekly_close_ema_cache/18_25_75/202210/20200101_20221017" + \
    "/close_ema_18_20200101_20221017^000030.gzip.pickle"
    src1 = "/Users/sam/data/stock/cache/hist_weekly_close_ema_cache/18_25_75/202210/20200101_20221018" + \
           "/close_ema_18_20200101_20221018^000030.gzip.pickle"
    # pickle2csv(src0, "/Users/sam/Desktop/17_close_ema_18^000030.xlsx")
    # pickle2csv(src1, "/Users/sam/Desktop/18_close_ema_18^000030.xlsx")

    src2 = "/Users/sam/data/stock/cache/hist_weekly_cache/202210/20200101_20221017" + \
           "/20200101_20221017^000030.gzip.pickle"

    src3 = "/Users/sam/data/stock/cache/hist_weekly_cache/202210/20200101_20221018" + \
           "/20200101_20221018^000030.gzip.pickle"
    src4 = "/Users/sam/data/stock/cache/hist_weekly_cache/202210/20200101_20221019" + \
           "/20200101_20221019^000030.gzip.pickle"
    pickle2csv(src2, "/Users/sam/Desktop/17_close_^000030.xlsx")
    pickle2csv(src3, "/Users/sam/Desktop/18_close_^000030.xlsx")
    pickle2csv(src4, "/Users/sam/Desktop/19_close_^000030.xlsx")
