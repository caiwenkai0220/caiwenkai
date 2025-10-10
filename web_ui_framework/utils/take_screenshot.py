import os.path
from datetime import datetime

from web_ui_framework.utils.logger import logger


def take_screenshot(driver, name='screenshot'):
    """截取屏幕截图"""
    try:
        # 确保截图目录存在
        screenshot_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),'screenshots')
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        # 生成唯一的截图文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{name}_{timestamp}.png'
        filepath = os.path.join(screenshot_dir,filename)

        # 截图并保存
        driver.save_screenshot(filepath)
        logger.info(f'截图已保存至：{filepath}')
        return filepath
    except Exception as e:
        logger.error(f'截图失败：{str(e)}')
        return None