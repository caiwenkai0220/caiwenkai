import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from web_ui_framework.utils.logger import logger
from web_ui_framework.configs.config import config


browser = config.browser
implicit_wait = config.implicit_wait


@pytest.fixture(scope='session')
def driver():
    """全局driver 整个测试会话只初始化一次"""
    logger.info(f'初始化浏览器：{browser}')
    if browser == 'chrome':
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser == 'safari':
        driver = webdriver.Safari()
    else:
        raise ValueError(f'不支持的浏览器：{browser}')

    # 设置隐式等待
    driver.implicitly_wait(implicit_wait)
    # 最大化窗口
    driver.maximize_window()

    logger.info(f'浏览器{browser}初始化完成')
    yield driver
    # 测试结束后，关闭浏览器
    driver.quit()
    logger.info(f'关闭浏览器：{browser}')

@pytest.fixture(autouse=True)
def test_setup_teardown(driver,request):
    """每个测试用例执行前后的setup和teardown"""
    logger.info(f'开始执行测试：{request.node.nodeid}')
    yield
    logger.info(f'测试执行完成：{request.node.nodeid}')