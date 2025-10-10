import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from utils.logger import logger
from web_ui_framework.pages.base_pages import BasePage


class DeviceModelPage(BasePage):
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
    edit_confirm_button = (By.CSS_SELECTOR,'.edit-one-form+div>span:nth-child(1)') # 保存编辑按钮
    edit_cancel_button = (By.CSS_SELECTOR,'.edit-one-form+div>span:nth-child(2)') # 取消编辑按钮

    # 2、元素操作
    def __init__(self, driver):
        super().__init__(driver)

    # 点击添加按钮
    def click_add_button(self):
        self.click(self.add_button)

    # 添加操作时，点击取消按钮
    def click_cancel_button(self):
        self.click(self.add_button)

    # 添加操作时，选择设备种类
    def select_device_class(self, text):
        self.select_by_text(self.device_class_select,text)

    # 添加操作时，输入设备型号
    def input_device_model(self, text):
        self.send_keys(self.device_model_input, text)

    # 添加操作时，输入型号描述
    def input_model_description(self, text):
        self.send_keys(self.model_description_input, text)

    # 编辑操作时，选择设备种类
    def edit_device_class(self, text):
        self.select_by_text(self.device_class_select,text)

    # 添加操作时，点击确认按钮
    def click_confirm_button(self):
        self.click(self.confirm_button)

    # 添加一个设备型号
    def add_one_device_model(self, class_text, model_text, description_text):
        self.click_add_button()
        self.select_device_class(class_text)
        self.input_device_model(model_text)
        self.input_model_description(description_text)
        self.click_confirm_button()

    # 获取列表某一行的类型值、设备型号值、描述，存入到列表并返回
    def get_nth_line_result(self, nth):  # nth为行数，从1开始
        result_list = []
        list_item = self.find_elements(self.nth_line_results)[nth-1]
        print(list_item)
        for ele in list_item.find_elements(By.CSS_SELECTOR, '.result-list-item-info .field-value'):
            print(ele)
            result_list.append(ele.text)
        return result_list

    # 删除一条设备型号
    def delete_one_device_model(self, model):  # model值为要删除的设备型号
        try:
            for index, ele in enumerate(self.find_elements(self.device_model_value)):
                if ele.text == model:
                    delete_button_ele = self.find_elements(self.delete_button)[index]
                    delete_button_ele.click()
                    self.accept_alert()
                    print('删除成功')
                    logger.info(f'删除设备型号 {model} 成功')
                    return index
            raise NoSuchElementException

        except NoSuchElementException:
            logger.error(f'删除失败，未找到设备型号：{model}')
            raise


    # 修改设备型号的信息
    def modify_one_device_model(self, model, new_class, new_model, new_desc):
        button_elements = self.find_elements(self.modify_button)
        for index, button in enumerate(button_elements):
            if self.find_element(self.device_model_value).text == model:
                button.click()
                self.select_by_text(self.edit_device_class_select, new_class)
                self.send_keys(self.edit_device_model_input,new_model)
                self.send_keys(self.edit_model_description_input,new_desc)
                self.click(self.edit_confirm_button)
                print('修改成功')
                return index
        print(f'没有{model}设备')
        return -1

    # 等待添加的设备出现在第一行设备列表中
    def wait_added_model_appear(self, text):
        first_model = (By.XPATH, f'(//div[@class="result-list-item-info"])[1]//span[@class="field-value"][text()="{text}"]')
        self.find_element(first_model)