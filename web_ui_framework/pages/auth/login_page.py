import time
from selenium.webdriver.common.by import By
from web_ui_framework.pages.base_pages import BasePage
from web_ui_framework.utils.logger import logger
from web_ui_framework.configs.config import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from web_ui_framework.pages.home.home_page import HomePage

# 创建登陆页面对象
class LoginPage(BasePage):

    username_css = (By.ID,'username')
    password_css = (By.ID,'password')
    login_button = (By.ID,'loginBtn')

    def __init__(self, driver):
        super().__init__(driver)
        self.login_url = f'{config.base_url}:8234/login.html'

    def open_login_page(self):
        # 打开登陆页面
        self.open_page(self.login_url)

    # 简化方法命名
    def input_username(self, username):
        self.send_keys(self.username_css, username)
        logger.info(f'输入用户名：{username}')  # 补充输入日志，方便追溯

    def input_password(self, password):
        self.send_keys(self.password_css, password)
        logger.info('输入密码：******')  # 密码脱敏，避免日志泄露

    # 点击登陆按钮
    def click_login_button(self):
        self.click(self.login_button,wait_for_url_change="index.html")
        logger.info("点击登录")

    # 完整登陆流程
    def login(self, username, password, expected_success=True):
        self.open_login_page()
        logger.info(f'开始登录，用户名：{username}')
        self.input_username(username)
        self.input_password(password)
        self.click_login_button()

        # 根据预期结果进行校验
        if expected_success:
            # 假设登录成功后跳转到首页，首页有特征元素（如用户名展示）
            try:
                # 等待首页元素出现，确认登录成功
                if self.is_logged_in():
                    logger.info(f'登录成功，用户名：{username}')
            except Exception as e:
                logger.error(f'登录失败，未跳转到首页：{str(e)}')
                raise Exception('登录失败') from None
        else:
            # 预期登录失败，等待弹窗错误提示
            try :
                self.wait_alert()
                logger.info(f"符合预期，出现错误弹窗提示：{self.get_alert_message()}")
                return self.get_alert_message()
            except:
                raise Exception("不符合预期，未出现错误弹窗提示") from None

    # 获取错误提示信息
    def get_alert_message(self):
        """获取登录弹窗错误提示"""
        try:
            # 尝试获取弹窗提示
            alert = self.wait_alert()
            return alert.text
        except Exception:
            # 弹窗不存在时，获取页面内错误元素
            raise Exception('未出现账号密码错误弹窗') from None

    def is_logged_in(self):
        """判断是否已登录（通过首页用户名展示校验）"""
        try:
            self.wait_element_contains_text((By.ID, 'top-right'), "1号超级管理员")
            return True
        except:
            return False



if __name__ == '__main__':
    service = ChromeService(executable_path="/Users/caiwenkai/My/PycharmProjects/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service)
    login_page = LoginPage(driver)
    home_page = HomePage(driver)
    login_page.login("byhy","sdfsdf")
    home_page.click_business_rules()
