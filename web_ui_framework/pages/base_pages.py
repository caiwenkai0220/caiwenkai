from selenium.common import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web_ui_framework.utils.logger import logger
from web_ui_framework.configs.config import config

# 创建基础页面类
class BasePage:
    """基础页面类，封装所有页面共有的方法"""

    # 设置实例属性，driver
    def __init__(self, driver):
        self.driver = driver  # 设置实例属性driver，所有子类共享
        self.explicit_wait = config.explicit_wait

    # 打开地址
    def open(self, url):
        """打开指定URL"""
        self.driver.get(url)
        logger.info(f'打开页面：{url}')

    # 显示等待查找元素，直到找到或者超时
    def find_element(self, locator):
        """查找单个元素，使用显式等待"""
        try:
            element = WebDriverWait(self.driver, self.explicit_wait).until(EC.presence_of_element_located(locator))
            logger.info(f'找到元素：{locator}')
            return element
        except TimeoutError:
            logger.error(f'超时，未找到元素：{locator}')  # 记录日志
            raise # 继续抛出异常，防止程序在有异常的情况下继续执行

    # 显示等待查找元素，直到找到或者超时
    def find_elements(self, locator):
        try:
            elements = WebDriverWait(self.driver, self.explicit_wait).until(EC.presence_of_all_elements_located(locator))
            logger.info(f'找到元素列表：{locator}')
            return elements
        except TimeoutError:
            logger.error(f'超时，未找到元素列表：{locator}')
            raise

    def find_element_in_parent_locator(self,parent_locator,child_locator):
        """在父元素下查找子元素"""
        try:
            parent_element = WebDriverWait(self.driver, self.explicit_wait).until(EC.presence_of_element_located(parent_locator))
            logger.info(f'找到父元素：{parent_locator}')

            child_element = parent_element.find_elements(*child_locator)
            logger.info(f'在父元素{parent_locator}下找到子元素：{child_locator}')
            return child_element

        except TimeoutError:
            if 'parent_element' not in locals():
                logger.error(f'超时，未找到父元素：{parent_locator}')
            else:
                logger.error(f'超时，未找到子元素：{child_locator}')
            raise

    def find_elements_in_parent_locator(self,parent_locator,child_locator):
        """在父元素下查找多个子元素"""
        try:
            parent_element = WebDriverWait(self.driver, self.explicit_wait).until(EC.presence_of_element_located(parent_locator))
            logger.info(f'找到父元素：{parent_locator}')

            child_elements = parent_element.find_elements(*child_locator)
            logger.info(f'在父元素{parent_locator}下找到子元素列表：{child_locator}')
            return child_elements

        except TimeoutError:
            if 'parent_element' not in locals():
                logger.error(f'超时，未找到父元素：{parent_locator}')
            else:
                logger.error(f'超时，未找到子元素列表：{child_locator}')
            raise

    # 点击元素
    def click(self, locator):
        element = self.find_element(locator)
        element.click()
        logger.info(f'点击元素：{locator}')

    # 输入框输入文本
    def send_keys(self,locator,text):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        logger.info(f'向元素 {locator} 输入文本：{text}')

    # 获取元素文本
    def get_text(self,locator):
        text= self.find_element(locator).text
        logger.info(f'元素{locator}的文本为：{text}')
        return text

    # 等待元素显示
    def is_displayed(self,locator):
        try:
            displayed = self.find_element(locator).is_displayed()
            logger.info(f'元素 {locator} 是否显示：{displayed}')
            return displayed
        except TimeoutError:
            logger.info(f'元素 {locator} 未显示')
            return False

    # 选择下拉框元素
    def select_by_text(self, locator, text):
        try:
            select = Select(self.find_element(locator))
            select.select_by_visible_text(text)
        except NoSuchElementException:
            logger.error(f'未找到设备类型为 {text} 的下拉框')
            raise

    def get_url(self):
        return self.driver.current_url

    # 等待弹窗出现
    def wait_alert(self):
        try:
            # 显式等待弹窗出现
            WebDriverWait(self.driver,10).until(EC.alert_is_present())
            # 获取弹窗对象
            alert = self.driver.switch_to.alert
            return alert
        except  TimeoutError:
            logger.error('等待10s仍未出现弹窗')
            raise
        except NoAlertPresentException:
            logger.error('当前没有alert弹窗')
            raise

    # 点击确弹窗认
    def accept_alert(self):
        self.wait_alert()
        self.driver.switch_to.alert.accept()

    # 点击确弹取消
    def dismiss_alert(self):
        self.wait_alert()
        self.driver.switch_to.alert.dismiss()

    # 等待元素包含特定文本
    def wait_element_contains_text(self,locator,text):
        WebDriverWait(self.driver,self.explicit_wait).until(EC.text_to_be_present_in_element(locator,text))

