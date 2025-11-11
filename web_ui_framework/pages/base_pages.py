import time
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, UnexpectedTagNameException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from web_ui_framework.utils.logger import logger
from web_ui_framework.configs.config import config
from selenium.webdriver.chrome.service import Service as ChromeService


# 创建基础页面类
class BasePage:
    """基础页面类，封装所有页面共有的方法"""

    # 设置实例属性，driver
    def __init__(self, driver):
        self.driver = driver  # 设置实例属性driver，所有子类共享
        self.explicit_wait = config.explicit_wait

    # 打开地址
    def navigate(self, url):
        """打开指定URL"""
        try:
            if self.driver.current_url == url:
                logger.info(f"当前页面url已是{url}，无需跳转")
                return
            self.driver.get(url)
            WebDriverWait(self.driver, self.explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logger.info(f'跳转到{url}页面')
        except TimeoutException:
            logger.warning(f"页面{url}加载超时")

    def refresh(self):
        self.driver.refresh()
        try:
            WebDriverWait(self.driver,self.explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            logger.info("刷新页面完成")
        except TimeoutException:
            logger.warning("刷新页面超时")

    # 显示等待查找元素，直到找到或者超时
    def find_element(self, locator, timeout=None):
        """查找单个元素，使用显式等待"""
        try:
            timeout = timeout or self.explicit_wait
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
            logger.debug(f'找到元素：{locator}')
            return element
        except TimeoutException:
            logger.error(f'超时，未找到元素：{locator}')  # 记录日志
            # 继续抛出异常，防止程序在有异常的情况下继续执行
            raise TimeoutException(f"元素定位超时: {locator}")  from None

    # 显示等待查找元素，直到找到或者超时
    def find_elements(self, locator, timeout=None):
        try:
            timeout = timeout or self.explicit_wait
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator))
            logger.debug(f'找到元素列表：{locator}')
            return elements
        except TimeoutException:
            logger.error(f'超时，未找到元素列表：{locator}')
            # 继续抛出异常，防止程序在有异常的情况下继续执行
            raise Exception(f"元素定位超时: {locator}")  from None  # 用 from None 屏蔽原始堆栈，避免终端打印过多信息

    def find_element_in_parent_locator(self, parent_locator, child_locator,timeout=None):
        """在父元素下查找子元素"""
        try:
            # 显示等待父元素
            timeout = timeout or self.explicit_wait
            parent_element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(parent_locator))
            logger.debug(f'找到父元素：{parent_locator}')

            # 显示等待子元素
            child_element = WebDriverWait(parent_element, timeout).until(
                EC.presence_of_element_located(child_locator))
            logger.debug(f'在父元素{parent_locator}下找到子元素：{child_locator}')
            return child_element

        except TimeoutException:
            if 'parent_element' not in locals():
                logger.error(f'超时，未找到父元素：{parent_locator}')
                # 继续抛出异常，防止程序在有异常的情况下继续执行
                raise Exception(f'超时，未找到父元素：{parent_locator}')  from None
            else:
                logger.error(f'超时，未找到子元素：{child_locator}')
                # 继续抛出异常，防止程序在有异常的情况下继续执行
                raise Exception(f'超时，未找到子元素：{child_locator}')  from None

    def find_elements_in_parent_locator(self, parent_locator, child_locator,timeout=None):
        """在父元素下查找多个子元素"""
        try:
            timeout = timeout or self.explicit_wait
            parent_element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(parent_locator))
            logger.debug(f'找到父元素：{parent_locator}')

            child_elements = WebDriverWait(parent_element, timeout).until(
                EC.presence_of_all_elements_located(child_locator))
            logger.debug(f'在父元素{parent_locator}下找到子元素列表：{child_locator}')
            return child_elements

        except TimeoutException:
            if 'parent_element' not in locals():
                logger.error(f'超时，未找到父元素：{parent_locator}')
                # 继续抛出异常，防止程序在有异常的情况下继续执行
                raise Exception(f'超时，未找到父元素：{parent_locator}')  from None
            else:
                logger.error(f'超时，未找到子元素：{child_locator}')
                # 继续抛出异常，防止程序在有异常的情况下继续执行
                raise Exception(f'超时，未找到子元素：{child_locator}')  from None

    # 点击元素
    def click(self, locator, wait_for_url_change=None, wait_for_element=None, timeout=None):
        """
        点击元素，支持页面加载等待

        Args:
            locator: 元素定位器
            wait_for_url_change: 等待URL包含特定内容 (str)
            wait_for_element: 等待某个元素出现 (locator)
            timeout: 自定义超时时间
        """
        timeout = timeout or self.explicit_wait

        try:
            # 1. 等待元素可点击
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )

            # 2. 执行点击
            element.click()
            logger.debug(f"点击元素: {locator}")

            # 3. 根据参数进行不同的等待
            if wait_for_url_change:
                # 等待URL变化
                WebDriverWait(self.driver, timeout).until(
                    lambda driver: wait_for_url_change in driver.current_url
                )
                logger.debug(f"页面跳转完成，URL包含: {wait_for_url_change}")

            elif wait_for_element:
                # 等待特定元素出现
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located(wait_for_element)
                )
                logger.debug(f"目标元素已加载: {wait_for_element}")

        except TimeoutException:
            if wait_for_url_change:
                logger.error(f"超时，点击元素{locator}, url没有变为{wait_for_url_change}")
                raise Exception(f"超时，点击元素{locator}, url没有变为{wait_for_url_change}") from None
            elif wait_for_element:
                logger.error(f"超时，点击元素{locator}, 元素{wait_for_element}没有出现")
                raise Exception(f"超时，点击元素{locator}, 元素{wait_for_element}没有出现") from None
            else:
                logger.error(f"超时，点击元素{locator}失败")
                raise
        except Exception as e:
            logger.error(f"点击元素失败: {locator}, 错误: {str(e)}")
            raise

    # 输入框输入文本
    def send_keys(self, locator, text, clear_first=True):
        element = self.find_element(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug(f"在元素{locator}输入文本{text}")

    # 获取元素文本
    def get_text(self, locator):
        text = self.find_element(locator).text
        logger.debug(f'元素{locator}的文本为：{text}')
        return text

    # 等待元素显示
    def is_displayed(self, locator, timeout=None):
        """获取元素状态，区分不同情况"""
        timeout = timeout or self.explicit_wait

        # 先检查元素是否存在
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
        except TimeoutException:
            logger.info(f'元素 {locator} 未找到')
            return False

        # 再检查元素是否可见（重新定位避免 Stale Element）
        try:
            WebDriverWait(self.driver, 0.5).until(  # 较短超时，因为元素已存在
                EC.visibility_of_element_located(locator)
            )
            logger.info(f'正常，元素 {locator} 存在且可见')
            return True
        except TimeoutException:
            logger.info(f'异常，元素 {locator} 存在但不可见')
            return False

    def is_not_displayed(self,locator,timeout=None):
        timeout = timeout or self.explicit_wait
        try:
            WebDriverWait(self.driver,timeout).until(EC.invisibility_of_element_located(locator))
            logger.info(f"正常，元素 {locator} 已不可见")
            return True
        except TimeoutException:
            logger.error(f"异常，元素 {locator} 仍可见")
            return False

    # 选择下拉框元素
    def select_by_text(self, locator, text):
        try:
            select = Select(self.find_element(locator))  # 若元素不是select标签，会抛UnexpectedTagNameException
            select.select_by_visible_text(text)
            logger.debug(f"下拉框选择：{text}")
        except UnexpectedTagNameException:
            logger.error(f'元素 {locator} 不是下拉框（select标签）')
            raise Exception(f'元素 {locator} 不是下拉框') from None
        except NoSuchElementException:
            logger.error(f'未找到文本为 {text} 的下拉框')
            raise Exception(f'未找到文本为 {text} 的下拉框') from None

    def get_url(self):
        return self.driver.current_url

    # 等待弹窗出现
    def wait_alert(self, timeout=None):
        timeout = timeout or self.explicit_wait
        try:
            # 显式等待弹窗出现
            alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            return alert
        except TimeoutException:
            logger.error('超时，未出现弹窗')
            raise Exception(f'超时，未出现弹窗')  from None  # 用 from None 屏蔽原始堆栈

    def accept_alert(self, timeout=None):
        try:
            alert = self.wait_alert(timeout)  # 接收wait_alert返回的弹窗对象
            alert.accept()  # 直接使用返回的alert对象，避免重复switch
            logger.debug('点击确认弹窗')
        except Exception as e:
            logger.error(f'点击确认弹窗失败: {str(e)}')
            raise  # 重新抛出异常，让调用者处理

    # 点击弹窗取消
    def dismiss_alert(self, timeout=None):
        try:
            alert = self.wait_alert(timeout)
            alert.dismiss()
            logger.info('点击取消弹窗')
        except Exception as e:
            logger.error(f'点击取消弹窗失败: {str(e)}')
            raise

    # 等待元素包含特定文本
    def wait_element_contains_text(self, locator, text, timeout=None):
        timeout = timeout or self.explicit_wait
        try:
            # 等待文本出现，返回等待结果（通常是元素对象）
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(locator, text)
            )
            logger.info(f'元素 {locator} 已包含文本: {text}')
            return True  # 返回True，明确等待成功
        except TimeoutException:
            logger.error(f'超时，元素 {locator} 未包含文本: {text}')
            raise Exception(f'元素 {locator} 未包含预期文本: {text}') from None

    def execute_script(self, script, *args):
        """执行JavaScript脚本"""
        try:
            result = self.driver.execute_script(script, *args)
            logger.debug(f"执行JavaScript: {script}")
            return result
        except Exception as e:
            logger.error(f"执行JavaScript失败: {script}, 错误: {str(e)}")
            raise

    def scroll_to_element(self, locator):
        """滚动到元素位置"""
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        logger.debug(f"滚动到元素: {locator}")


if __name__ == '__main__':
    service = ChromeService(executable_path="/Users/caiwenkai/My/PycharmProjects/PythonProject/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service)
    basepage = BasePage(driver)
    button = (By.CSS_SELECTOR, "#loginBtns")
    basepage.open_page("http://127.0.0.1:8234/login.html")
    basepage.is_displayed(button)
    time.sleep(1)
