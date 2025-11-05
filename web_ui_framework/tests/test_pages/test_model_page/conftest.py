import pytest

# 显式声明，继承父级conftest
pytest_plugins = ["tests.test_pages.conftest"]

@pytest.fixture
def device_model_page(home_page):
    return home_page.click_device_model()

@pytest.fixture(autouse=True)
def refresh_page(device_model_page):
    device_model_page.refresh()
    yield

@pytest.fixture
def setup_add_device(device_model_page):
    # 定义一个内部函数，接收参数
    def _add_device(device_class,device_model,model_description):
        device_model_page.add_one_device_model(device_class,device_model,model_description)
        return [device_class,device_model,model_description]
    yield _add_device

@pytest.fixture
def teardown_delete_device(device_model_page):
    # 存储需要删除的设备型号
    models_to_delete = []
    def _delete_device(device_model):
        # 用例中调用此方法，保存需要删除的型号
        models_to_delete.append(device_model)
    yield _delete_device
    # 测试用例执行完后，再开始删除所有要删除的设备型号
    for model in models_to_delete:
        device_model_page.delete_one_device_model(model)

# @pytest.fixture
# def setup_and_teardown(device_model_page):
#     device = []
#     def _add_and_delete_device(device_class,device_model,model_description):
#         device_model_page.add_one_device_model(device_class, device_model, model_description)
#         device.append(device_model)
#         return [device_class,device_model,model_description]
#     yield _add_and_delete_device
#     device_model_page.delete_one_device_model(device[0])


@pytest.fixture
def temporary_device(device_model_page):
    """上下文管理器风格的fixture"""
    devices_to_cleanup = []

    def create_temporary_device(device_class, device_model, model_description):
        # 创建设备
        device_model_page.add_one_device_model(device_class, device_model, model_description)
        device_data = {
            'class': device_class,
            'model': device_model,
            'description': model_description
        }
        devices_to_cleanup.append(device_data)
        return device_data

    yield create_temporary_device

    # 自动清理所有临时设备
    for device in devices_to_cleanup:
        try:
            device_model_page.delete_one_device_model(device['model'])
        except Exception as e:
            pytest.fail(f"清理设备失败: {e}")