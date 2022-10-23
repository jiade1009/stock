import logging
from logging import handlers
from qmtclient import base_config


# 创建日志记录器
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 设置日志输出格式
logFormat = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

# 创建一个Handler用于将日志写入文件
logFile = base_config.log_file
# 每隔500字节保存成一个日志文件，备份文件为5个
# fh = handlers.RotatingFileHandler(logFile, maxBytes=500, backupCount=3)
# 每隔1个小时，保存一个日志文件，备份文件为3个
fh = handlers.TimedRotatingFileHandler(logFile, encoding='utf-8', when="D", interval=1, backupCount=7)
# mode是文件的打开方式。默认是’a’，即添加到文件末尾。
# fh = logging.FileHandler(logFile, mode='a', encoding='utf-8')
fh.setLevel(logging.INFO)
fh.setFormatter(logFormat)

logger.addHandler(fh)

# 同样的，创建一个Handler用于控制台输出日志
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logFormat)
logger.addHandler(ch)
