import pytest
from utils.logger import logger
import allure

@pytest.fixture(autouse=True)
def init_url(home_page):
    home_page.navigate(home_page.home_page_url)
    logger.info(f"已进入{home_page.home_page_url}页面")

class TestHomePage:

    def test_url(self,home_page):
        assert home_page.get_url() == home_page.home_page_url


    def test_click_device_model(self,home_page):
        home_page.click_device_model()
        assert home_page.get_url() == f"{home_page.home_page_url}#/devicemodel"


    def test_click_business_rules(self,home_page):
        home_page.click_business_rules()
        assert home_page.get_url() == f"{home_page.home_page_url}#/svcrule"


