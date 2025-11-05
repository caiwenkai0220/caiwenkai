import time

import pytest



class TestDeviceModelPage:

    def test_click_add_button(self,device_model_page):
        device_model_page.click_add_button()
        assert device_model_page.is_displayed(device_model_page.device_class_select)

    def test_cancel_add_button(self,device_model_page):
        device_model_page.click_add_button()
        device_model_page.wait_element_contains_text(device_model_page.add_button,'取消')
        device_model_page.click_cancel_button()
        assert device_model_page.wait_element_contains_text(device_model_page.add_button,'添加')

    def test_add_device_model(self,device_model_page):
        device_model_page.add_one_device_model('洗车站','AD360','专门洗公路车')
        first_line_result = device_model_page.get_nth_line_result(1)
        assert first_line_result == ['洗车站','AD360','专门洗公路车']

    def test_delete_device_model(self,device_model_page):
        device_model_page.delete_one_device_model('AD360')
        assert device_model_page.wait_model_disappear('AD360')

    def test_midify_device_model(self,device_model_page):
        row = device_model_page.get_nth_by_model('123')
        device_model_page.modify_one_device_model('123','洗车站','A200','全自动洗车')
        assert device_model_page.get_nth_line_result(row) == ['洗车站','A200','全自动洗车']