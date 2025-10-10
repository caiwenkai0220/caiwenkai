
class TestBusinessRulesPage:
    def test_click_business_rules(self,business_rules_page):
        assert business_rules_page.get_url() == 'http://127.0.0.1:8234/index.html#/svcrule'
