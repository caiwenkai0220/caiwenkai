

class TestHomePage:

    def test_click_device_model(self,home_page):
        home_page.click_device_model()
        assert home_page.get_url() == "http://127.0.0.1:8234/index.html#/devicemodel"


