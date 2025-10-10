import pytest

# 显式声明，继承父级conftest
pytest_plugins = ["tests.test_pages.conftest"]

@pytest.fixture
def device_model_page(home_page):
    return home_page.click_device_model()

@pytest.fixture(autouse=True)
def init_page(home_page):
    home_page.click_business_rules()
    home_page.click_device_model()