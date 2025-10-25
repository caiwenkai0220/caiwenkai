import logging
import os
from web_ui_framework.configs.config import config

# 确保日志目录存在
log_dir = os.path.join((os.path.dirname(os.path.dirname(__file__))), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 日志配置
log_level = config.log_level
log_file = os.path.join(log_dir,config.log_file) # 确保这里是完整的日志文件路径（如os.path.join(log_dir, 'test.log')）
# 日志格式
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(lineno)s - %(levelname)s - %(message)s')

# 全局日志器
logger = logging.getLogger('web_ui_test')
logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
logger.propagate = False  # 禁止向父日志器传递

def add_handler_if_not_exist(handler_type, handler_args, formatter):
    # 检查是否已有同类型处理器
    handler_exists = any(isinstance(h, handler_type) for h in logger.handlers)
    if not handler_exists:
        try:
            # 明确处理无参数的情况（如StreamHandler）
            if handler_args is None:
                new_handler = handler_type()
            else:
                new_handler = handler_type(handler_args)
            new_handler.setFormatter(formatter)
            new_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            logger.addHandler(new_handler)
            print(f"已添加处理器：{type(new_handler).__name__}")  # 调试信息
        except Exception as e:
            print(f"添加处理器失败：{e}")  # 捕获可能的异常

# 添加文件处理器
# add_handler_if_not_exist(logging.FileHandler, log_file, formatter)
# 添加控制台处理器
add_handler_if_not_exist(logging.StreamHandler, None, formatter)


if __name__ == '__main__':
    print("当前处理器：", [type(h).__name__ for h in logger.handlers])
    logger.error("哈哈哈")