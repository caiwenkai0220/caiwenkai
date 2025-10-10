from selenium.webdriver.common.by import By
from web_ui_framework.pages.base_pages import BasePage
from web_ui_framework.utils.logger import logger


# 创建登陆页面对象
class LoginPage(BasePage):

    username = (By.ID,'username')
    password = (By.ID,'password')
    login_button = (By.ID,'loginBtn')

    def __init__(self, driver):
        super().__init__(driver)
        self.login_url = f'{self.config['test_env']['base_url']}:8234/login.html'

    def load(self):
        # 打开登陆页面
        self.open(self.login_url)

    # 输入用户名
    def enter_username(self,username):
        self.send_keys(self.username, username)

    # 输入密码
    def enter_password(self, password):
        self.send_keys(self.password, password)

    # 点击登陆按钮
    def click_login_button(self):
        self.click(self.login_button)

    # 完整登陆流程
    def login(self,username,password):
        self.load()
        logger.info(f'执行登陆操作，用户名：{username}')
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()

    # 获取错误提示信息
    def get_error_message(self):
        alert = self.wait_alert()
        return alert.text



