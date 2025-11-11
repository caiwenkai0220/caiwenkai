import pytest


# 显式声明继承父级conftest
# pytest_plugins = ["tests.test_pages.conftest"]  # 关键行

@pytest.fixture
def device_model_page(home_page):
    return home_page.click_device_model()

@pytest.fixture(autouse=True)
def refresh_page(device_model_page):
    device_model_page.refresh()
    yield



class DeviceManager:
    def __init__(self, device_model_page):
        self.device_model_page = device_model_page
        self.devices_to_cleanup = []

    def create_device(self, device_class, device_model, model_description):
        """创建设备"""
        self.device_model_page.add_one_device_model(device_class, device_model, model_description)
        device_data = {
            'class': device_class,
            'model': device_model,
            'description': model_description
        }
        self.devices_to_cleanup.append(device_data)
        return device_data

    def delete_device(self, device_model, timeout=0.1):
        """删除指定型号的设备"""
        try:
            if not self.device_model_page.wait_model_disappear(device_model,timeout):
                self.device_model_page.delete_one_device_model(device_model)
                # 从清理列表中移除
                self.devices_to_cleanup = [d for d in self.devices_to_cleanup if d['model'] != device_model]
        except Exception as e:
            pytest.fail(f"删除设备失败: {e}")

    def cleanup_all(self,timeout=0.1):
        """清理所有设备"""
        for device in self.devices_to_cleanup[:]:  # 使用副本遍历
            try:
                if not self.device_model_page.wait_model_disappear(device['model'],timeout):
                    self.device_model_page.delete_one_device_model(device['model'])
            except Exception as e:
                pytest.fail(f"清理设备失败: {e}")
        self.devices_to_cleanup.clear()

@pytest.fixture
def device_manager(device_model_page):
    """设备管理器fixture"""
    manager = DeviceManager(device_model_page)
    yield manager
    manager.cleanup_all()