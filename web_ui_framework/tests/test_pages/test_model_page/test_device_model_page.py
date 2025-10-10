from selenium.webdriver.common.by import By


class TestDeviceModelPage:

    def test_click_add_button(self,device_model_page):
        device_model_page.click_add_button()
        assert device_model_page.is_displayed(device_model_page.device_class_select)

    def test_cancel_add_button(self,device_model_page):
        device_model_page.click_add_button()
        device_model_page.wait_element_contains_text(device_model_page.add_button,'取消')
        device_model_page.click_cancel_button()
        assert not device_model_page.find_element((By.CSS_SELECTOR,'.add-one-form')).is_displayed()

    def test_add_device_model(self,device_model_page):
        device_model_page.add_one_device_model('洗车站','AD360','专门洗公路车')
        device_model_page.wait_added_model_appear('AD360')
        first_line_result = device_model_page.get_nth_line_result(1)
        assert first_line_result == ['洗车站','AD360','专门洗公路车']

    def test_delete_device_model(self,device_model_page):
        index = device_model_page.delete_one_device_model('电瓶车充电站')
        assert device_model_page.find_elements(device_model_page.device_model_value)[index] != '电瓶车充电站'

    def test_failed_to_delete_device_model(self,device_model_page):
        index = device_model_page.delete_one_device_model('电瓶车充电站')
        assert index == -1

    def test_midify_device_model(self,device_model_page):
        device_model_page.modify_one_device_model('123','洗车站','A100','全自动洗车')
        device_model_page.wait_added_model_appear('A100')
        assert device_model_page.get_nth_line_result(1) == ['洗车站','A100','全自动洗车']