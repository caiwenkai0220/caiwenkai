import os
import yaml

class Config:
    def __init__(self):
        # 读取yaml配置文件
        config_path = os.path.join(os.path.dirname(__file__),"config.yaml")
        with open(config_path) as f:
            self.config = yaml.safe_load(f)


        # 解析配置项为属性
        self.default = self.config.get("default",{})
        self.test_env = self.config.get("test_env",{})
        self.logging = self.config.get("logging",{})

    # 将方法变为属性，能直接使用config.browser获取配置的browser
    @property
    def browser(self):
        return self.default.get("browser","chrome")

    @property
    def implicit_wait(self):
        return int(self.default.get("implicit_wait", 5)) # 记得加int，否则返回字符串

    @property
    def explicit_wait(self):
        return int(self.default.get("explicit_wait", 5))  # 记得加int，否则返回字符串

    @property
    def base_url(self):
        return self.test_env.get("base_url", "http://127.0.0.1")

    @property
    def username(self):
        return self.test_env.get("username", "byhy")

    @property
    def password(self):
        return self.test_env.get("password", "sdfsdf")

    @property
    def log_level(self):
        return self.logging.get("log_level", "INFO")

    @property
    def log_file(self):
        return self.logging.get("log_file", "test.log")

config = Config()

if __name__ == '__main__':
    config = Config()
    print(config.password)