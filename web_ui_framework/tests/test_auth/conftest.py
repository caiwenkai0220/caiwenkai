import pytest
from selenium.common import NoAlertPresentException
from web_ui_framework.utils.logger import logger

# pytest_plugins = ["tests.conftest"]
# 私有函数，如果出现弹窗就关闭
def _dismiss_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        logger.info('关闭弹窗')
    except NoAlertPresentException:
        pass # 无弹窗就跳过

@pytest.fixture(autouse=True)
def auto_close_alert(driver):
    yield
    _dismiss_alert(driver)  # 自动关闭弹窗