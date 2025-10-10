import configparser
import os
import pytest
from web_ui_framework.pages.auth.login_page import LoginPage
from web_ui_framework.pages.home.home_page import HomePage

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'configs','config.ini'))
username = config['test_env']['username']
password = config['test_env']['password']

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

