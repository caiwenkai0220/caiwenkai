from selenium.webdriver.common.by import By

from web_ui_framework.pages.base_pages import BasePage
from web_ui_framework.pages.home.tab.business_rules_page import BusinessRulesPage
from web_ui_framework.pages.home.tab.device_model_page import DeviceModelPage


class HomePage(BasePage):
    device_model_menu = (By.CSS_SELECTOR,'.sub-nav-bar a[href="#/devicemodel"]')
    business_rules_menu = (By.CSS_SELECTOR,'.sub-nav-bar a[href="#/svcrule"]')
    device_menu = (By.CSS_SELECTOR,'.sub-nav-bar a[href="#/device"]')
    customer_menu = (By.CSS_SELECTOR,'.sub-nav-bar a[href="#/customer"]')
    consumption_record_menu = (By.CSS_SELECTOR,'.sub-nav-bar a[href="#/svcrecord"]')
    user_menu = (By.CSS_SELECTOR,'#top-right')
    logout_menu = (By.CSS_SELECTOR,'.dropdown-menu>li:nth-of-type(2)')

    def __init__(self, driver):
        super().__init__(driver)

    def click_user(self):
        self.click(self.user_menu)

    def logout(self):
        self.click_user()
        self.click(self.logout_menu)


    def click_device_model(self):
        self.click(self.device_model_menu)
        return DeviceModelPage(self.driver)  # 点击设备型号菜单，同时创建设备型号tab页对象，并返回

    def click_business_rules(self):
        self.click(self.business_rules_menu)
        return BusinessRulesPage(self.driver)  # 点击业务规则菜单，同时创建业务规则tab页对象，并返回

