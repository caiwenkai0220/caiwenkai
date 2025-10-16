import pytest
from web_ui_framework.pages.auth.login_page import LoginPage
from web_ui_framework.pages.home.home_page import HomePage
from web_ui_framework.configs.config import config

username = config.username
password = config.password

# 显式声明继承父级conftest
pytest_plugins = ["tests.conftest"]  # 关键行

@pytest.fixture(scope='package')
def logged_in_session(driver):
    login_page = LoginPage(driver)
    login_page.load()
    login_page.login(username,password)

@pytest.fixture()
def home_page(driver,logged_in_session):
    yield HomePage(driver)

