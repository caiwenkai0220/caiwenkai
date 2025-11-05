import pytest

pytest_plugins = ["tests.test_pages.conftest"]

@pytest.fixture
def business_rules_page(home_page):
    return home_page.click_business_rules()

