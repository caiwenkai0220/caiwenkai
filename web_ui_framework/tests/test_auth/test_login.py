import allure

from pages.home.home_page import HomePage
from pages.auth.login_page import LoginPage

from configs.config import config

# 读取配置文件
username = config.username
password = config.password


class TestLogin:
    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("正确账号密码登录")  # 用例标题
    @allure.description("前置条件：用户未登录；执行步骤：输入正确账号正确密码登录；预期结果：应可以登录成功")  # 用例步骤
    @allure.severity(allure.severity_level.BLOCKER)  # 优先级，阻塞级别，相当于P0
    @allure.tag("冒烟测试", "主流程")  # 自定义标签，支持多维度筛选
    @allure.testcase("https://jira.example.com/browse/TEST-001", "用例ID：TEST-001")  # 关联Jira用例
    def test_successful_login_01(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"1、打开登录页面，输入正确用户名:{username},正确密码:{password}, 点击登录"):
            login_page.login(username,password)
        with allure.step(f"2、断言登录成功，页面标题变为：E生活"):
            assert driver.title == 'E生活'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("退出登录")  # 自定义标题
    @allure.description("前置条件：用户已登录；执行步骤：点击退出登录；预期结果：应退出到登录界面")
    @allure.severity(allure.severity_level.BLOCKER)  # 阻塞级别，相当于P0
    @allure.tag("冒烟测试","核心功能")
    @allure.testcase("https://jira.example.com/browse/TEST-002", "用例ID：TEST-002")
    def test_logout_02(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"1、输入正确用户名:{username},正确密码:{password}, 进行登录"):
            login_page.login(username,password)
        home_page = HomePage(driver)
        with allure.step(f"2、点击退出登录"):
            home_page.logout()
        with allure.step(f"3、断言退出登录成功，页面url变为：http://127.0.0.1:8234/login.html"):
            assert home_page.get_url() == 'http://127.0.0.1:8234/login.html'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("错误密码登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入正确账号错误密码登录；预期结果：应弹窗提示 用户名或者密码错误")
    @allure.severity(allure.severity_level.CRITICAL)  # 严重级别，相当于P1
    @allure.tag("冒烟测试", "主流程")
    @allure.testcase("https://jira.example.com/browse/TEST-003", "用例ID：TEST-003")  # 关联Jira用例
    def test_failed_login_03(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"输入正确用户名:{username},错误密码:sdfsd, 点击登录"):
            login_page.login(username, 'sdfsd', expected_success=False)
        with allure.step(f"断言登录失败，弹窗提示为：'登录失败： 用户名或者密码错误'"):
            assert login_page.get_alert_message() == '登录失败： 用户名或者密码错误'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("错误账号登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入错误账号，正确密码登录；预期结果：应弹窗提示 用户名不存在")
    @allure.severity(allure.severity_level.NORMAL)  # 普通级别，相当于P2
    @allure.tag("非主流程")
    @allure.testcase("https://jira.example.com/browse/TEST-004", "用例ID：TEST-004")
    def test_failed_login_04(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"1、输入错误用户名:byh,正确密码:{password}, 点击登录"):
            login_page.login('byh', password, expected_success=False)
        with allure.step(f"2、断言登录失败，弹窗提示为：'登录失败： 用户名不存在'"):
            assert login_page.get_alert_message() == '登录失败： 用户名不存在'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("错误账号错误密码登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入错误账号，错误密码登录；预期结果：应弹窗提示 用户名不存在")
    @allure.severity(allure.severity_level.NORMAL)  # 普通级别，相当于P2
    @allure.tag("非主流程")
    @allure.testcase("https://jira.example.com/browse/TEST-005", "用例ID：TEST-005")
    def test_failed_login_05(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"1、输入错误用户名：byh，错误密码：sdfsd，点击登录"):
            login_page.login('byh', 'sdfsd', expected_success=False)
        with allure.step(f"2、断言登录失败，弹窗提示为：'登录失败： 用户名不存在'"):
            assert login_page.get_alert_message() == '登录失败： 用户名不存在'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("未输入用户名登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：未输入用户名，输入密码登录；预期结果：应弹窗提示 请输入用户名")
    @allure.severity(allure.severity_level.NORMAL)  # 普通级别，相当于P2
    @allure.tag("非主流程")
    @allure.testcase("https://jira.example.com/browse/TEST-006", "用例ID：TEST-006")
    def test_failed_login_06(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"1、不输入用户名，输入密码：{password}，点击登录"):
            login_page.login('', password='sdfsd', expected_success=False)
        with allure.step(f"2、断言登录失败，弹窗提示为：'请输入用户名'"):
            assert login_page.get_alert_message() == '请输入用户名'

    @allure.feature("登录")  # 大模块
    @allure.story("账号密码登录")  # 子功能
    @allure.title("未输入密码登录")  # 自定义标题
    @allure.description("前置条件：用户未登录；执行步骤：输入用户名，不输入密码登录；预期结果：应弹窗提示 请输入密码")
    @allure.severity(allure.severity_level.NORMAL)  # 普通级别，相当于P2
    @allure.tag("非主流程")
    @allure.testcase("https://jira.example.com/browse/TEST-007", "用例ID：TEST-007")
    def test_failed_login_07(self,driver):
        login_page = LoginPage(driver)
        with allure.step(f"1、输入用户名: {username}，不输入密码，点击登录"):
            login_page.login('byhy', password='', expected_success=False)
        with allure.step(f"2、断言登录失败，弹窗提示为：'请输入密码'"):
            assert login_page.get_alert_message() == '请输入密码'
