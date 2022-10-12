import logging

# 创建日志记录器
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 设置日志输出格式
logFormat = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

# 创建一个Handler用于将日志写入文件
logFile = '/Users/sam/Documents/IdeaProjects/stock/web/log.txt'
fh = logging.FileHandler(logFile, mode='a', encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(logFormat)
logger.addHandler(fh)

# 同样的，创建一个Handler用于控制台输出日志
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logFormat)
logger.addHandler(ch)
