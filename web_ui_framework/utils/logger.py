import logging
import os
import configparser
from datetime import datetime

# 确保日志目录存在,如果没有就创建目录
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 读取配置文件
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(__file__)),'configs','config.ini'))

# 日志配置
log_level = config['logging']['log_level']
log_file = os.path.join(log_dir,config['logging']['log_file'])


# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建日志记录器
logger = logging.getLogger('web_ui_test')
logger.setLevel(getattr(logging,log_level.upper(),logging.INFO))

# 创建文件处理器
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

# 创建控制台处理器
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)
# logger.addHandler(console_handler)