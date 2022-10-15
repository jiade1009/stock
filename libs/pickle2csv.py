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
    src1 = "/Users/sam/data/stock/cache/hist_weekly_ema_cache/18_25_75/202209/20200101_20220901" + \
    "/close_ema_18_20200101_20220901^000001.gzip.pickle"
    pickle2csv(src1, "/Users/sam/Desktop/close_ema_18^000001.xlsx")

    src2 = "/Users/sam/data/stock/cache/hist_weekly_cache/202209/20200101_20220901" + \
           "/20200101_20220901^000001.gzip.pickle"
    pickle2csv(src2, "/Users/sam/Desktop/close_^000001.xlsx")
