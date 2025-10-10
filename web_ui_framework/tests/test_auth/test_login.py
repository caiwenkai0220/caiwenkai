import configparser
import os
from time import sleep

import pytest

from pages.home.home_page import HomePage
from web_ui_framework.pages.auth.login_page import LoginPage
from web_ui_framework.utils.take_screenshot import take_screenshot

# 读取配置文件
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'configs','config.ini'))
username = config['test_env']['username']
password = config['test_env']['password']


class TestLogin:
    def test_successful_login(self,driver):
        login_page = LoginPage(driver)
        login_page.login(username,password)
        sleep(1)
        assert driver.title == 'E生活'
        take_screenshot(driver)

    def test_failed_login1(self,driver):
        login_page = LoginPage(driver)
        login_page.login('byh', password)
        assert login_page.get_error_message() == '登录失败： 用户名不存在'

    def test_failed_login2(self,driver):
        login_page = LoginPage(driver)
        login_page.login(username, 'sdfsd')
        assert login_page.get_error_message() == '登录失败： 用户名或者密码错误'

    def test_failed_login3(self,driver):
        login_page = LoginPage(driver)
        login_page.login('byh', 'sdfsd')
        assert login_page.get_error_message() == '登录失败： 用户名不存在'

    def test_failed_login4(self,driver):
        login_page = LoginPage(driver)
        login_page.login('', password='sdfsd')
        assert login_page.get_error_message() == '请输入用户名'

    def test_failed_login5(self,driver):
        login_page = LoginPage(driver)
        login_page.login('byhy', password='')
        assert login_page.get_error_message() == '请输入密码'

    def test_logout(self,driver):
        login_page = LoginPage(driver)
        login_page.login(username,password)
        home_page = HomePage(driver)
        home_page.logout()
        assert home_page.get_url() == 'http://127.0.0.1:8234/login.html'