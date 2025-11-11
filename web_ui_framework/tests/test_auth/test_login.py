

from pages.home.home_page import HomePage
from web_ui_framework.pages.auth.login_page import LoginPage

from web_ui_framework.configs.config import config

# 读取配置文件
username = config.username
password = config.password


class TestLogin:
    def test_successful_log_01(self,driver):
        login_page = LoginPage(driver)
        login_page.login(username,password)
        assert driver.title == 'E生活'

    def test_failed_login_02(self,driver):
        login_page = LoginPage(driver)
        login_page.login('byh', password, expected_success=False)
        assert login_page.get_alert_message() == '登录失败： 用户名不存在'

    def test_failed_login_03(self,driver):
        login_page = LoginPage(driver)
        login_page.login(username, 'sdfsd', expected_success=False)
        assert login_page.get_alert_message() == '登录失败： 用户名或者密码错误'

    def test_failed_login_04(self,driver):
        login_page = LoginPage(driver)
        login_page.login('byh', 'sdfsd', expected_success=False)
        assert login_page.get_alert_message() == '登录失败： 用户名不存在'

    def test_failed_login_05(self,driver):
        login_page = LoginPage(driver)
        login_page.login('', password='sdfsd', expected_success=False)
        assert login_page.get_alert_message() == '请输入用户名'

    def test_failed_login_06(self,driver):
        login_page = LoginPage(driver)
        login_page.login('byhy', password='', expected_success=False)
        assert login_page.get_alert_message() == '请输入密码'

    def test_logout_07(self,driver):
        login_page = LoginPage(driver)
        login_page.login(username,password)
        home_page = HomePage(driver)
        home_page.logout()
        assert home_page.get_url() == 'http://127.0.0.1:8234/login.html'