
class TestDeviceModelPage:

    def test_click_add_button(self,device_model_page):
        device_model_page.click_add_button()
        assert device_model_page.is_displayed(device_model_page.device_class_select)

    def test_cancel_add_button(self,device_model_page):
        device_model_page.click_add_button()
        device_model_page.wait_element_contains_text(device_model_page.add_button,'取消')
        device_model_page.click_cancel_button()
        assert device_model_page.wait_element_contains_text(device_model_page.add_button,'添加')

    def test_add_device_model(self,device_model_page,device_manager):
        device_model_page.add_one_device_model('洗车站','AD370','自动化测试')
        first_line_result = device_model_page.get_nth_line_result(1)
        assert first_line_result == ['洗车站','AD370','自动化测试']
        device_manager.delete_device("AD370")

    def test_delete_device_model(self,device_model_page,device_manager):
        device_manager.create_device('洗车站','哈哈','全自动洗车')
        assert device_model_page.delete_one_device_model("哈哈")

    def test_midify_device_model(self,device_model_page,device_manager):
        device_manager.create_device('洗车站', 'AD370', '全自动洗车')
        device_model_page.modify_one_device_model("AD370",'洗车站','A200','全自动洗车')
        assert device_model_page.get_nth_line_result(1) == ['洗车站','A200','全自动洗车']
        device_manager.delete_device("A200")

