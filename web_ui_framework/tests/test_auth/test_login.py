import allure

from pages.home.home_page import HomePage
from web_ui_framework.pages.auth.login_page import LoginPage

from web_ui_framework.configs.config import config

# 读取配置文件
username = config.username
password = config.password


class TestLogin:
    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("登录成功")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入正确账号正确密码登录；预期结果：应可以登录成功")
    @allure.severity(allure.severity_level.BLOCKER)  # 阻塞级别，相当于P0
    @allure.tag("冒烟测试", "核心功能")
    @allure.link("https://docs.example.com/login", "登录功能文档")
    def test_successful_log_01(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"输入正确用户名:{username},正确密码:{password}, 进行登录"):
            login_page.login(username,password)
        with allure.step(f"断言是否登录成功，页面标题是否是：E生活"):
            assert driver.title == 'E生活'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("错误账号登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入错误账号，正确密码登录；预期结果：应可以登录成功")
    @allure.severity(allure.severity_level.NORMAL)  # 普通级别，相当于P2
    @allure.tag("冒烟测试", "核心功能")
    @allure.link("https://docs.example.com/login", "登录功能文档")
    def test_failed_login_02(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"输入错误用户名:byh,正确密码:{password}, 进行登录"):
            login_page.login('byh', password, expected_success=False)
        with allure.step(f"断言登录失败，弹窗提示为：'登录失败： 用户名不存在'"):
            assert login_page.get_alert_message() == '登录失败： 用户名不存在'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("错误密码登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入正确账号错误密码登录；预期结果：应可以登录成功")
    @allure.severity(allure.severity_level.CRITICAL)  # 严重级别，相当于P1
    @allure.tag("冒烟测试", "核心功能")
    @allure.link("https://docs.example.com/login", "登录功能文档")
    def test_failed_login_03(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"输入正确用户名:{username},错误密码:sdfsd, 进行登录"):
            login_page.login(username, 'sdfsd', expected_success=False)
        with allure.step(f"断言登录失败，弹窗提示为：'登录失败： 用户名或者密码错误'"):
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
        with allure.step(f"输入正确用户名:{username},正确密码:{password}, 进行登录"):
            login_page.login(username,password)
        home_page = HomePage(driver)
        with allure.step(f"点击退出登录"):
            home_page.logout()
        with allure.step(f"断言退出登录成功，页面url变为：http://127.0.0.1:8234/login.html"):
            assert home_page.get_url() == 'http://127.0.0.1:8234/login.html'