import time

from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from configs.config import config
from utils.logger import logger
from web_ui_framework.pages.base_pages import BasePage


class DeviceModelPage(BasePage):
    device_model_page_url = f"{config.base_url}:{config.port}/index.html"
    # 1、元素定位
    # 添加元素定位
    add_button = (By.CSS_SELECTOR, '.add-one-area>.btn:nth-child(1)')  # 添加按钮
    cancel_button = (By.XPATH, '//*[@class="btn"][text()="取消"]')  # 取消按钮
    device_class_select = (By.CSS_SELECTOR, '#device-type')  # 设备种类选择框
    device_model_input = (By.CSS_SELECTOR, '#device-model')  # 设备型号输入框
    model_description_input = (By.CSS_SELECTOR, '#device-model-desc')  # 型号描述输入框
    confirm_button = (By.CSS_SELECTOR, '.add-one-submit-btn-div .btn')  # 确认按钮

    # 列表元素定位
    nth_line_results = (By.CSS_SELECTOR, '.result-list>.result-list-item')  # 列表所有的行
    nth_line_values = (By.CSS_SELECTOR, '.result-list-item-info .field-value')  # 每行的设备类型、设备型号、描述的值
    delete_button = (By.CSS_SELECTOR, '.result-list-item-btn-bar>span:nth-child(1)')  # 定位设备型号的所有删除按钮
    modify_button = (By.CSS_SELECTOR, '.result-list-item-btn-bar>span:nth-child(2)')  # 定位设备型号的所有修改按钮
    device_model_value = (By.CSS_SELECTOR, '.result-list-item-info>div:nth-child(2)>.field-value')  # 列表所有设备型号的值

    # 修改元素定位
    edit_device_class_select = (By.CSS_SELECTOR, '.result-list-item .edit-one-form select')
    edit_device_model_input = (By.CSS_SELECTOR, '.edit-one-form>div:nth-child(2)>input')
    edit_model_description_input = (By.CSS_SELECTOR, '.edit-one-form>div:nth-child(3)>input')
    edit_confirm_button = (By.CSS_SELECTOR, '.edit-one-form+div>span:nth-child(1)')  # 保存编辑按钮
    edit_cancel_button = (By.CSS_SELECTOR, '.edit-one-form+div>span:nth-child(2)')  # 取消编辑按钮

    # 2、元素操作
    def __init__(self, driver):
        super().__init__(driver)

    # 点击添加按钮
    def click_add_button(self):
        self.click(self.add_button)
        logger.info("点击添加按钮")

    # 添加操作时，点击取消按钮
    def click_cancel_button(self):
        self.click(self.add_button)
        logger.info("点击取消按钮")

    # 添加操作时，选择设备种类
    def select_device_class(self, text):
        self.select_by_text(self.device_class_select, text)
        logger.info(f"选择添加设备种类：{text}")

    # 添加操作时，输入设备型号
    def input_device_model(self, text):
        self.send_keys(self.device_model_input, text)
        logger.info(f"输入设备型号：{text}")

    # 添加操作时，输入型号描述
    def input_model_description(self, text):
        self.send_keys(self.model_description_input, text)
        logger.info(f"选择设备型号描述：{text}")

    # 编辑操作时，选择设备种类
    def edit_device_class(self, text):
        self.select_by_text(self.device_class_select, text)
        logger.info(f"选择编辑设备种类：{text}")

    # 添加操作时，点击确定按钮
    def click_confirm_button(self):
        self.click(self.confirm_button)
        logger.info("点击确定按钮")

    # 添加一个设备型号
    def add_one_device_model(self, class_text, model_text, description_text,timeout=None):
        self.click_add_button()
        self.select_device_class(class_text)
        self.input_device_model(model_text)
        self.input_model_description(description_text)
        self.click_confirm_button()
        if self.wait_model_appear(model_text,timeout):
            logger.info(f"添加设备型号 {model_text} 成功")
        else:
            logger.error(f"添加设备型号 {model_text} 失败")

    # 获取列表某一行的类型值、设备型号值、描述，存入到列表并返回
    def get_nth_line_result(self, nth):  # nth为行数，从1开始
        if nth < 1:
            raise ValueError("行数必须大于1")
        self.refresh()
        lists = self.find_elements(self.nth_line_results)
        if not lists or nth > len(lists):
            raise IndexError(f"第{nth}行不存在，总共{len(lists)}行")
        nth_line = lists[nth-1]
        filed_elements = nth_line.find_elements(By.CSS_SELECTOR, '.result-list-item-info .field-value')
        result_list = [ele.text for ele in filed_elements]
        logger.info(f"第{nth}行的内容为：{result_list}")
        return result_list

    # 通过设备型号，获取对应行数
    def get_nth_by_model(self,model):
        self.refresh()
        model_values = self.find_elements(self.device_model_value)
        for index,ele in enumerate(model_values):
            if ele.text == model:
                logger.info(f"设备型号{model}，在第{index + 1}行")
                return index+1
        raise Exception(f"未找到设备型号: {model}")

    # 删除一条设备型号
    def delete_one_device_model(self, model, timeout=None):  # model值为要删除的设备型号
        timeout = timeout or self.explicit_wait
        model_selector = (By.XPATH, f'//span[@class="field-value"][text()="{model}"]')
        delete_selector = (By.XPATH,
                           f'//span[@class="field-value"][text()="{model}"]/../../..//span[@class="btn-no-border"][1]')
        if self.find_element(model_selector):
            self.click(delete_selector)
            logger.info(f"点击删除按钮：{delete_selector}")
            self.accept_alert()
            logger.info(f"点击弹窗确认")
            if self.wait_model_disappear(model,timeout):
                logger.info(f'删除设备型号 {model} 成功')
                return True
            else:
                logger.warning(f'删除设备型号 {model} 失败')
                return False

        else:
            logger.error(f'删除失败，未找到设备型号：{model}')
            raise Exception(f'删除失败，未找到设备型号：{model}')

    # 修改设备型号的信息
    def modify_one_device_model(self, model, new_class, new_model, new_desc,timeout=None):
        timeout = timeout or self.explicit_wait
        model_selector = (By.XPATH, f'//span[@class="field-value"][text()="{model}"]')
        modify_selector = (By.XPATH,
                           f'//span[@class="field-value"][text()="{model}"]/../../..//span[@class="btn-no-border"][2]')
        if self.find_element(model_selector):
            self.click(modify_selector)
            logger.info(f"点击修改按钮{modify_selector}")
            self.select_by_text(self.edit_device_class_select, new_class)
            logger.info(f"选择设备种类：{new_class}")
            self.send_keys(self.edit_device_model_input, new_model)
            logger.info(f"输入设备型号：{new_model}")
            self.send_keys(self.edit_model_description_input, new_desc)
            logger.info(f"输入设备描述：{new_desc}")
            self.click(self.edit_confirm_button)
            logger.info(f"点击确认按钮：{self.edit_confirm_button}")
            self.wait_model_disappear(model,timeout)
            self.wait_model_appear(new_model)
            logger.info(f'修改设备型号 {model} 成功')

        else:
            logger.error(f'修改失败，未找到设备型号：{model}')
            raise Exception(f'修改失败，未找到设备型号：{model}')

    def wait_model_appear(self, model_text,timeout=None):
        try:
            timeout = timeout or self.explicit_wait
            model_selector = (By.XPATH,
                              f'//div[@class="result-list-item-info"]//div[@class="field"][2]//span[text()="{model_text}"]')
            self.find_element(model_selector,timeout)
            logger.info(f"设备型号 {model_text} 已出现在列表中")
            return True
        except TimeoutException:
            logger.warning(f"设备型号 {model_text} 未出现在列表中")
            return False

    def wait_model_disappear(self, model_text, timeout=None):
        try:
            timeout = timeout or self.explicit_wait
            model_selector = (By.XPATH,
                              f'//div[@class="result-list-item-info"]//div[@class="field"][2]//span[text()="{model_text}"]')
            # 临时将隐式等待设置为0
            self.driver.implicitly_wait(0.1)
            WebDriverWait(self.driver, timeout, poll_frequency=0.1).until(
                lambda driver: len(driver.find_elements(*model_selector)) == 0
            )
            # 恢复原来的隐式等待
            self.driver.implicitly_wait(config.implicit_wait)

            logger.info(f"设备型号 {model_text} 已不在列表中")
            return True
        except TimeoutException:
            logger.warning(f"设备型号 {model_text} 还在列表中")
            return False