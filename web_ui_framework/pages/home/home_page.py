import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService

from web_ui_framework.pages.auth.login_page import LoginPage
from web_ui_framework.pages.base_pages import BasePage
from web_ui_framework.pages.home.tab.business_rules_page import BusinessRulesPage
from web_ui_framework.pages.home.tab.device_model_page import DeviceModelPage
from web_ui_framework.utils.logger import logger
from web_ui_framework.configs.config import config

class HomePage(BasePage):
    device_model_menu = (By.CSS_SELECTOR, '.sub-nav-bar a[href="#/devicemodel"]')  # 设备型号
    business_rules_menu = (By.CSS_SELECTOR, '.sub-nav-bar a[href="#/svcrule"]')  # 业务规则
    device_menu = (By.CSS_SELECTOR, '.sub-nav-bar a[href="#/device"]')  # 设备
    customer_menu = (By.CSS_SELECTOR, '.sub-nav-bar a[href="#/customer"]')  # 客户
    consumption_record_menu = (By.CSS_SELECTOR, '.sub-nav-bar a[href="#/svcrecord"]')  # 消费记录
    user_menu = (By.CSS_SELECTOR, '#top-right')  # 1号超级管理员
    dropdown_menu = (By.CSS_SELECTOR, ".dropdown-menu")  # 1号超级管理员下的菜单
    logout_menu = (By.CSS_SELECTOR, '.dropdown-menu>li:nth-of-type(2)')  # 退出
    home_page_url = f"{config.base_url}:{config.port}/index.html"

    def __init__(self, driver):
        super().__init__(driver)

    def click_user(self):
        self.click(self.user_menu)
        logger.info("点击1号超级管理员")
        self.is_displayed(self.dropdown_menu)
        logger.info("出现下拉菜单")

    def logout(self):
        self.click_user()
        self.click(self.logout_menu, wait_for_url_change="login.html")
        logger.info("点击退出")
        try:
            WebDriverWait(self.driver, self.explicit_wait).until(lambda driver: "login.html" in driver.current_url)
            logger.info("退出登录成功")
            return True
        except TimeoutError:
            logger.error(f"退出登录失败，当前url为：{self.get_url()}")
            return False

    def click_device_model(self, url="devicemodel", timeout=None):
        logger.info("点击设备型号")
        self.click(self.device_model_menu, wait_for_url_change=url, timeout=timeout)
        logger.info("成功进入设备型号页面")
        return DeviceModelPage(self.driver)  # 点击设备型号菜单，同时创建设备型号tab页对象，并返回

    def click_business_rules(self, url="svcrule", timeout=None):
        logger.info("点击业务规则")
        self.click(self.business_rules_menu, wait_for_url_change=url, timeout=timeout)
        logger.info("成功进入业务规则页面")
        return BusinessRulesPage(self.driver)  # 点击业务规则菜单，同时创建业务规则tab页对象，并返回

if __name__ == '__main__':
    service = ChromeService(executable_path="/Users/caiwenkai/My/PycharmProjects/PythonProject/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service)
    login_page = LoginPage(driver)
    login_page.login("byhy", "sdfsdf")
    home_page = HomePage(driver)
    time.sleep(1)
    # device_model_page = home_page.click_device_model()
    # # device_model_page.add_one_device_model("电瓶车充电站","ChgStation4","自动化测试添加设备型号4")
    # result = device_model_page.get_nth_by_model("123")
    # # device_model_page.modify_one_device_model("1203zxc","电瓶车充电站","特斯拉model-Y","40W")