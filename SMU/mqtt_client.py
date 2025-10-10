import json
import time
import logging
import threading
from paho.mqtt import client as mqtt_client


class MQTTClient:
    """MQTT客户端类，用于平台与SMU之间的通信"""
    #
    def __init__(self, broker, port, client_id):
        """初始化MQTT客户端

        Args:
            broker: MQTT broker地址
            port: MQTT端口
            client_id: 客户端ID

        """
        self.logger = logging.getLogger(__name__)
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.client = None
        self.connected = False
        self.response = None
        self.response_event = threading.Event()
        self.command_topic = ""
        self.response_topic = ""

    def connect(self, command_topic, response_topic):
        """连接到MQTT broker并订阅响应主题

        Args:
            command_topic: 发送命令的主题
            response_topic: 接收响应的主题

        Returns:
            连接成功返回True，否则返回False
        """
        self.command_topic = command_topic
        self.response_topic = response_topic

        # 创建MQTT客户端
        self.client = mqtt_client.Client(self.client_id)

        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        # 连接到broker
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()  # 启动网络循环线程

            # 等待连接成功
            start_time = time.time()
            while not self.connected and time.time() - start_time < 10:
                time.sleep(0.1)

            if self.connected:
                self.logger.info(f"MQTT连接成功: {self.broker}:{self.port}")
                return True
            else:
                self.logger.error("MQTT连接超时")
                return False

        except Exception as e:
            self.logger.error(f"MQTT连接错误: {str(e)}")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        """连接回调函数"""
        if rc == 0:
            self.connected = True
            # 订阅响应主题
            self.client.subscribe(self.response_topic)
            self.logger.info(f"已订阅响应主题: {self.response_topic}")
        else:
            self.logger.error(f"MQTT连接失败，错误代码: {rc}")

    def _on_message(self, client, userdata, msg):
        """消息接收回调函数"""
        try:
            payload = json.loads(msg.payload.decode())
            self.logger.debug(f"收到MQTT消息 [{msg.topic}]: {payload}")

            # 如果是我们关注的响应主题，保存响应并触发事件
            if msg.topic == self.response_topic:
                self.response = payload
                self.response_event.set()

        except json.JSONDecodeError:
            self.logger.error(f"无法解析MQTT消息: {msg.payload.decode()}")
        except Exception as e:
            self.logger.error(f"处理MQTT消息错误: {str(e)}")

    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调函数"""
        self.connected = False
        self.logger.warning(f"MQTT连接已断开，错误代码: {rc}")

        # 尝试重新连接
        if rc != 0:
            self.logger.info("尝试重新连接MQTT...")
            self.connect(self.command_topic, self.response_topic)

    def send_command(self, command, params=None, timeout=5):
        """发送命令到SMU并等待响应

        Args:
            command: 命令名称
            params: 命令参数(字典)
            timeout: 等待响应的超时时间(秒)

        Returns:
            响应数据(字典)，超时或错误返回None
        """
        if not self.connected:
            self.logger.error("MQTT未连接，无法发送命令")
            return None

        # 重置响应和事件
        self.response = None
        self.response_event.clear()

        # 构建命令消息
        message = {
            "command": command,
            "params": params or {},
            "timestamp": time.time()
        }

        try:
            # 发送消息
            result = self.client.publish(
                self.command_topic,
                json.dumps(message)
            )

            # 检查发布结果
            status = result[0]
            if status != 0:
                self.logger.error(f"无法发送命令到主题 {self.command_topic}")
                return None

            self.logger.debug(f"已发送命令到 {self.command_topic}: {message}")

            # 等待响应
            if self.response_event.wait(timeout):
                return self.response
            else:
                self.logger.warning(f"等待命令响应超时 ({timeout}秒)")
                return None

        except Exception as e:
            self.logger.error(f"发送MQTT命令错误: {str(e)}")
            return None

    def disconnect(self):
        """断开MQTT连接"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.logger.info("MQTT连接已断开")
