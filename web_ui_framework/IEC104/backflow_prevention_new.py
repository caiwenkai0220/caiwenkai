import socket
import struct
import time
import threading
import logging

# 简易日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from typing import Tuple, Optional, Dict


# 设备状态管理类（单例）
class DeviceState:
    def __init__(self):
        self.lock = threading.Lock()
        # 设备功率状态：统一COA=1，{功率IOA: 功率值}
        # IOA=1: PCS, IOA=2: 逆变器, IOA=3: 电表(自动计算)
        self.device_power: Dict[int, Dict[int, float]] = {
            1: {1: 0.0, 2: 0.0, 3: 0.0}
        }

    def update_device_power(self, coa: int, ioa: int, value: float):
        """更新设备功率值，电表会自动计算"""
        with self.lock:
            # 仅更新PCS(IOA=1)或逆变器(IOA=2)
            if coa == 1 and ioa in (1, 2):
                self.device_power[coa][ioa] = value
                # 自动计算电表功率(IOA=3)
                pcs_power = self.device_power[1][1]
                inverter_power = self.device_power[1][2]
                self.device_power[1][3] = pcs_power + inverter_power
                logger.info(
                    f"设备功率更新 - PCS(IOA=1): {pcs_power} | 逆变器(IOA=2): {inverter_power} | 电表(IOA=3): {self.device_power[1][3]}")

    def get_device_power(self, coa: int, ioa: int) -> float:
        """获取设备功率值"""
        with self.lock:
            return self.device_power.get(coa, {}).get(ioa, 0.0)

    def reset_all(self):
        """重置所有设备功率"""
        with self.lock:
            self.device_power = {
                1: {1: 0.0, 2: 0.0, 3: 0.0}
            }


# 全局设备状态实例
device_state = DeviceState()


# 配置类
class IEC104Config:
    HOST = "127.0.0.1"
    PORT = 2404
    CA_DEFAULT = 0x01
    SEQ_STEP = 2  # 序号递增步长
    CLIENT_TIMEOUT = 30.0
    MAX_CLIENTS = 5

    # 允许连接的客户端白名单
    ALLOWED_CLIENT_IPS = ["127.0.0.1", "192.168.1.100"]  # 示例IP，替换为你的目标IP


# IEC104协议常量定义
class IEC104Const:
    START_BYTE = 0x68
    M_TYPE_YX = 0x01  # 遥信
    M_TYPE_YC_FLOAT = 0x0D  # 短浮点遥测
    M_TYPE_YC_SCALED = 0x0B  # 标度化遥测
    M_TYPE_YM = 0x0F  # 遥脉

    M_TYPE_INTERROGATION = 0x64  # 总召
    M_TYPE_SINGLE_CMD = 0x2D  # 单点遥控
    M_TYPE_REGULATE_CMD = 0x30  # 归一化遥调
    M_TYPE_SCALED_CMD = 0x31  # 标度值遥调
    M_TYPE_FLOAT_CMD = 0x32  # 浮点值遥调

    # 传输原因(COT)
    COT_SPONTANEOUS = 0x03  # 自发
    COT_INTERROGATED = 0x14  # 总召响应
    COT_ACTIVATION = 0x07  # 激活确认
    COT_ACTIVATION_TERMINATION = 0x0A  # 激活终止

    CA_DEFAULT = IEC104Config.CA_DEFAULT
    CONTROL_FIELD_LEN = 4

    # U帧固定控制头
    U_FRAME_LINK_START = b"\x68\x04\x07\x00\x00\x00"
    U_FRAME_LINK_START_ACK = b"\x68\x04\x0B\x00\x00\x00"
    U_FRAME_LINK_TEST = b"\x68\x04\x43\x00\x00\x00"
    U_FRAME_LINK_TEST_ACK = b"\x68\x04\x83\x00\x00\x00"


class IEC104Server:
    def __init__(self, host: str = IEC104Config.HOST, port: int = IEC104Config.PORT):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.client_sockets = {}
        self.client_lock = threading.Lock()

        # 序号管理（线程安全）
        self.seq_lock = threading.Lock()
        self.last_client_ns = 0x0000  # 主站最后一次发送的Ns
        self.last_client_nr = 0x0000  # 主站最后一次的Nr
        self.current_server_ns = 0x0000  # 服务器当前发送的Ns
        self.seq_step = IEC104Config.SEQ_STEP

        # 新增：总召完成标记（线程安全）
        self.total_interrogation_done = threading.Event()  # 初始为False
        # 新增：服务器启动完成标记（解决时序问题核心）
        self.server_started = threading.Event()  # 初始为False

    # ---------------------- 等待客户端Socket（核心优化） ----------------------
    def wait_client_socket(self, target_ip: str = None, target_port: int = None, timeout: float = 60.0) -> Optional[
        socket.socket]:
        start_time = time.time()
        if not self.server_started.wait(timeout=min(10.0, timeout)):
            logger.error("服务器启动超时，无法等待客户端连接")
            return None

        while self.running:
            if time.time() - start_time > timeout:
                logger.error(f"等待客户端连接超时（{timeout}秒）")
                return None

            client_socket = self.get_client_socket(target_ip, target_port)
            if client_socket:
                return client_socket
            time.sleep(0.5)

        logger.warning("服务器已停止，终止等待客户端连接")
        return None

    # ---------------------- 等待总召完成 ----------------------
    def wait_total_interrogation(self, timeout: float = 60.0) -> bool:
        if self.total_interrogation_done.is_set():
            return True

        logger.info(f"等待总召完成（超时={timeout}秒）...")
        wait_result = self.total_interrogation_done.wait(timeout if timeout > 0 else None)

        if wait_result:
            logger.info("✅ 总召已完成")
            return True
        else:
            logger.error(f"等待总召完成超时（{timeout}秒）")
            return False

    # ---------------------- 自动获取客户端Socket ----------------------
    def get_client_socket(self, target_ip: str = None, target_port: int = None) -> Optional[socket.socket]:
        with self.client_lock:
            if not self.client_sockets:
                logger.warning("无已连接的客户端")
                return None

            if target_ip and target_port:
                target_addr = (target_ip, target_port)
                if target_addr in self.client_sockets:
                    return self.client_sockets[target_addr]
                logger.warning(f"客户端 {target_addr} 未连接")
                return None

            elif target_ip:
                for addr, sock in self.client_sockets.items():
                    if addr[0] == target_ip:
                        logger.info(f"自动匹配IP={target_ip}的客户端：{addr}")
                        return sock
                logger.warning(f"无IP={target_ip}的已连接客户端")
                return None

            else:
                first_addr, first_sock = next(iter(self.client_sockets.items()))
                return first_sock

    # ---------------------- 简化发送方法（等待连接+等待总召） ----------------------
    def send_yx(self, value: int, ioa: int, ca: int = 1, target_ip: str = None, target_port: int = None,
                timeout: float = 60.0):
        client_socket = self.wait_client_socket(target_ip, target_port, timeout)
        if not client_socket:
            logger.error(f"发送遥信失败（IOA={ioa}, 值={value}）：未获取到客户端Socket")
            return

        if not self.wait_total_interrogation(timeout):
            logger.error(f"发送遥信失败（IOA={ioa}, 值={value}）：总召未完成（超时）")
            return

        self.send_yx_message(client_socket, value, ioa, ca)

    def send_yc_float(self, value: float, ioa: int, ca: int = 1, target_ip: str = None, target_port: int = None,
                      timeout: float = 60.0):
        client_socket = self.wait_client_socket(target_ip, target_port, timeout)
        if not client_socket:
            logger.error(f"发送浮点遥测失败（IOA={ioa}, 值={value}）：未获取到客户端Socket")
            return

        if not self.wait_total_interrogation(timeout):
            logger.error(f"发送浮点遥测失败（IOA={ioa}, 值={value}）：总召未完成（超时）")
            return

        self.send_yc_float_message(client_socket, value, ioa, ca)

    def send_yc_scaled(self, value: int, ioa: int, ca: int = 1, target_ip: str = None, target_port: int = None,
                       timeout: float = 60.0):
        client_socket = self.wait_client_socket(target_ip, target_port, timeout)
        if not client_socket:
            logger.error(f"发送标度遥测失败（IOA={ioa}, 值={value}）：未获取到客户端Socket")
            return

        if not self.wait_total_interrogation(timeout):
            logger.error(f"发送标度遥测失败（IOA={ioa}, 值={value}）：总召未完成（超时）")
            return

        self.send_yc_scaled_message(client_socket, value, ioa, ca)

    def send_ym(self, value: int, ioa: int, ca: int = 1, target_ip: str = None, target_port: int = None,
                timeout: float = 60.0):
        client_socket = self.wait_client_socket(target_ip, target_port, timeout)
        if not client_socket:
            logger.error(f"发送遥脉失败（IOA={ioa}, 值={value}）：未获取到客户端Socket")
            return

        if not self.wait_total_interrogation(timeout):
            logger.error(f"发送遥脉失败（IOA={ioa}, 值={value}）：总召未完成（超时）")
            return

        self.send_ym_message(client_socket, value, ioa, ca)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(IEC104Config.MAX_CLIENTS)
            self.running = True
            self.server_started.set()
            logger.info(f"104服务器启动：{self.host}:{self.port}")
            logger.info(f"仅允许以下IP连接：{IEC104Config.ALLOWED_CLIENT_IPS}")  # 打印白名单
            logger.info("模拟设备：统一COA=1，PCS(IOA=1)、逆变器(IOA=2)、电表(IOA=3)")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_ip = client_address[0]  # 提取客户端IP

                    # 核心：IP白名单校验
                    if client_ip not in IEC104Config.ALLOWED_CLIENT_IPS:
                        logger.warning(f"拒绝非法IP连接：{client_ip}（不在白名单 {IEC104Config.ALLOWED_CLIENT_IPS}）")
                        client_socket.close()  # 直接关闭连接
                        continue  # 跳过后续处理

                    # 合法IP，加入客户端列表
                    with self.client_lock:
                        self.client_sockets[client_address] = client_socket
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    logger.info(f"新客户端连接：{client_address}，当前连接数：{len(self.client_sockets)}")
                except socket.error as e:
                    if self.running:
                        logger.error(f"客户端连接失败：{e}")
        except Exception as e:
            logger.error(f"服务器异常：{e}", exc_info=True)
            self.server_started.set()
        finally:
            self.stop_server()

    # ---------------------- 解析主站报文序号 ----------------------
    def _parse_client_seq(self, data: bytes) -> Tuple[int, int]:
        """
        解析主站报文的Ns（发送序号）和Nr（接收序号）
        :param data: 主站发送的完整报文
        :return: (client_ns, client_nr)
        """
        if len(data) < 6:
            logger.warning("报文长度不足，无法解析序号")
            return 0x0000, 0x0000

        # IEC104控制头结构：68 + 长度 + Ns(2字节) + Nr(2字节)
        # 仅处理I帧（U帧无序号）
        control_byte1 = data[2]
        if (control_byte1 & 0x80) == 0x80:  # U帧标识
            logger.debug("收到U帧，无序号信息")
            return 0x0000, 0x0000

        # 解析Ns（主站发送序号）和Nr（主站接收序号）
        client_ns = int.from_bytes(data[2:4], byteorder='little')
        client_nr = int.from_bytes(data[4:6], byteorder='little')

        # 线程安全更新序号缓存
        with self.seq_lock:
            self.last_client_ns = client_ns
            self.last_client_nr = client_nr
            self.current_server_ns = client_nr  # 服务器Ns从主站Nr开始

        logger.debug(f"解析主站序号：Ns=0x{client_ns:04X}, Nr=0x{client_nr:04X}")
        return client_ns, client_nr

    # ---------------------- 生成发送序号（确保Nr=主站Ns+2） ----------------------
    def _get_send_seq(self) -> Tuple[int, int]:
        """
        生成服务器发送的Ns和Nr：
        - Ns：服务器自增序号（从主站Nr开始）
        - Nr：主站Ns + 2（确认已收到主站报文）
        """
        with self.seq_lock:
            # Nr = 主站最后一次Ns + 2（模65536）
            server_nr = (self.last_client_ns + self.seq_step) & 0xFFFF
            # Ns = 服务器当前发送序号（自增2）
            server_ns = self.current_server_ns
            self.current_server_ns = (self.current_server_ns + self.seq_step) & 0xFFFF

        logger.debug(f"生成发送序号：服务器Ns=0x{server_ns:04X}, 确认Nr=0x{server_nr:04X}")
        return server_ns, server_nr

    def _calc_length_field(self, asdu_len: int) -> int:
        return IEC104Const.CONTROL_FIELD_LEN + asdu_len

    def _build_control_header(self, asdu_len: int) -> bytes:
        len_field = self._calc_length_field(asdu_len)
        server_ns, server_nr = self._get_send_seq()
        ns_bytes = server_ns.to_bytes(2, byteorder='little')
        nr_bytes = server_nr.to_bytes(2, byteorder='little')
        control_header = bytes([IEC104Const.START_BYTE, len_field]) + ns_bytes + nr_bytes
        logger.debug(f"构建控制头：{control_header.hex()}")
        return control_header

    # ---------------------- 处理遥控报文时先解析序号 ----------------------
    def process_message(self, client_socket: socket.socket, data: bytes, client_address: Tuple[str, int]):
        try:
            if len(data) < 2 or data[0] != IEC104Const.START_BYTE:
                logger.warning(f"{client_address} 非法报文：{data.hex()}")
                return

            # 第一步：先解析主站报文的序号（所有I帧都要解析）
            self._parse_client_seq(data)
            # 1、判断是否是启动报文
            if data == IEC104Const.U_FRAME_LINK_START:
                self.handle_link_start(client_socket)
            # 2、判断是否是测试报文
            elif data == IEC104Const.U_FRAME_LINK_TEST:
                self.handle_test(client_socket)
            elif len(data) == 6 and data[2] == 0x01:
                self.handle_record_nr()
            elif len(data) > 6:
                m_type = data[6]
                logger.debug(f"报文类型：0x{m_type:02X}")
                # 3、判断是否是总召唤报文
                if m_type == IEC104Const.M_TYPE_INTERROGATION:
                    self.handle_total_interrogation(client_socket)
                # 4、判断是否是遥控报文
                elif m_type == IEC104Const.M_TYPE_SINGLE_CMD:
                    if len(data) > 15:
                        cmd_flag = data[15]
                        # 判断是遥控选择
                        if cmd_flag in (0x80, 0x81):
                            self.handle_yk_select(client_socket, data)
                        # 判断是遥控执行
                        if cmd_flag in (0x00, 0x01):
                            # 解析序号后再处理遥控回复，确保Nr正确
                            self.handle_yk_exec(client_socket, data)
                # 5、判断是标度化遥调报文
                elif m_type == IEC104Const.M_TYPE_SCALED_CMD:
                    if len(data) > 17:
                        cmd_flag = data[17]
                        # 判断是标度化遥调选择
                        if cmd_flag == 0x80:
                            self.handle_scaled_yt_select(client_socket, data)
                        # 判断是标度化遥调执行
                        elif cmd_flag == 0x00:
                            self.handle_scaled_yt_exec(client_socket, data)
                # 6、判断是浮点遥调报文
                elif m_type == IEC104Const.M_TYPE_FLOAT_CMD:
                    if len(data) > 19:
                        cmd_flag = data[19]
                        # 判断是短浮点遥调选择
                        if cmd_flag == 0x80:
                            self.handle_float_yt_select(client_socket, data)
                        # 判断是短浮点遥调执行
                        elif cmd_flag == 0x00:
                            self.handle_float_yt_exec(client_socket, data)
                else:
                    logger.warning(f"{client_address} 未处理报文类型：0x{m_type:02X}")
            else:
                logger.warning(f"{client_address} 无效I帧：{data.hex()}")
        except Exception as e:
            logger.error(f"{client_address} 报文处理异常：{e}", exc_info=True)

    def send_message(self, client_socket: socket.socket, message: bytes, desc: str = ""):
        try:
            client_socket.sendall(message)
            hex_str = '-'.join([f"{b:02X}" for b in message])
            logger.info(f"发送 [{desc}]：{hex_str}")
        except socket.error as e:
            logger.error(f"发送失败 [{desc}]：{e}")

    def send_i_frame(self, client_socket: socket.socket, asdu: bytes, desc: str = "I帧") -> Optional[bytes]:
        try:
            control_header = self._build_control_header(len(asdu))
            i_frame = control_header + asdu
            self.send_message(client_socket, i_frame, desc)
            return i_frame
        except Exception as e:
            logger.error(f"发送I帧失败 [{desc}]：{e}", exc_info=True)
            return None

    def _ioa_to_bytes(self, ioa: int) -> bytes:
        ioa = ioa & 0xFFFFFF
        return bytes([ioa & 0xFF, (ioa >> 8) & 0xFF, (ioa >> 16) & 0xFF])

    def _ca_to_bytes(self, ca: int, little_endian: bool = True) -> bytes:
        ca = ca & 0xFFFF
        low = ca & 0xFF
        high = (ca >> 8) & 0xFF
        return bytes([low, high]) if little_endian else bytes([high, low])

    def send_yx_message(self, client_socket: socket.socket, yx_value: int, ioa: int, ca: int = 1):
        yx_data = struct.pack('<B', yx_value & 0xFF)
        ioa_bytes = self._ioa_to_bytes(ioa)
        ca_bytes = self._ca_to_bytes(ca)
        asdu = struct.pack('<B B B B',
                           IEC104Const.M_TYPE_YX,
                           0x01,
                           IEC104Const.COT_SPONTANEOUS,
                           0x00
                           ) + ca_bytes + ioa_bytes + yx_data
        self.send_i_frame(client_socket, asdu, f"遥信(COA={ca}, IOA=0x{ioa:06X}, 值={yx_value})")

    def send_yc_float_message(self, client_socket: socket.socket, float_value: float, ioa: int, ca: int = 1):
        float_bytes = struct.pack('<f B', float_value, 0x00)
        ioa_bytes = self._ioa_to_bytes(ioa)
        ca_bytes = self._ca_to_bytes(ca)
        asdu = struct.pack('<B B B B',
                           IEC104Const.M_TYPE_YC_FLOAT,
                           0x01,
                           IEC104Const.COT_SPONTANEOUS,
                           0x00
                           ) + ca_bytes + ioa_bytes + float_bytes
        self.send_i_frame(client_socket, asdu, f"短浮点遥测(COA={ca}, IOA=0x{ioa:06X}, 值={float_value})")

    def send_yc_scaled_message(self, client_socket: socket.socket, scaled_value: int, ioa: int, ca: int = 1):
        scaled_value = scaled_value & 0xFFFFFF
        scaled_data = struct.pack('<I', scaled_value)[:3]
        ioa_bytes = self._ioa_to_bytes(ioa)
        ca_bytes = self._ca_to_bytes(ca)
        asdu = struct.pack('<B B B B',
                           IEC104Const.M_TYPE_YC_SCALED,
                           0x01,
                           IEC104Const.COT_SPONTANEOUS,
                           0x00
                           ) + ca_bytes + ioa_bytes + scaled_data
        self.send_i_frame(client_socket, asdu, f"标度化遥测(COA={ca}, IOA=0x{ioa:06X}, 值={scaled_value})")

    def send_ym_message(self, client_socket: socket.socket, ym_value: int, ioa: int, ca: int = 1):
        ym_data = struct.pack('<I B', ym_value & 0xFFFFFFFF, 0x00)
        ioa_bytes = self._ioa_to_bytes(ioa)
        ca_bytes = self._ca_to_bytes(ca)
        asdu = struct.pack('<B B B B',
                           IEC104Const.M_TYPE_YM,
                           0x01,
                           IEC104Const.COT_SPONTANEOUS,
                           0x00
                           ) + ca_bytes + ioa_bytes + ym_data
        self.send_i_frame(client_socket, asdu, f"遥脉(COA={ca}, IOA=0x{ioa:06X}, 值={ym_value})")

    def handle_link_start(self, client_socket: socket.socket):
        self.send_message(client_socket, IEC104Const.U_FRAME_LINK_START_ACK, "链路启动确认")

    def handle_test(self, client_socket: socket.socket):
        self.send_message(client_socket, IEC104Const.U_FRAME_LINK_TEST_ACK, "链路测试确认")

    @staticmethod
    def handle_record_nr():
        logger.info("收到记录nr报文")

    def handle_total_interrogation(self, client_socket: socket.socket):
        asdu1 = struct.pack('<B B B B 2B 3B B',
                            IEC104Const.M_TYPE_INTERROGATION,
                            0x01,
                            IEC104Const.COT_ACTIVATION,
                            0x00,
                            0xFF, 0xFF,
                            0x00, 0x00, 0x00,
                            0x14)
        self.send_i_frame(client_socket, asdu1, "总召激活确认")
        time.sleep(0.5)

        # 总召时主动上报所有设备的当前功率（统一COA=1，不同IOA）
        for ioa in [1, 2, 3]:
            power = device_state.get_device_power(1, ioa)
            self.send_yc_float_message(client_socket, power, ioa, 1)
            time.sleep(0.1)

        asdu3 = struct.pack('<B B B B 2B 3B B',
                            IEC104Const.M_TYPE_INTERROGATION,
                            0x01,
                            IEC104Const.COT_ACTIVATION_TERMINATION,
                            0x00,
                            0xFF, 0xFF,
                            0x00, 0x00, 0x00,
                            0x14)
        self.send_i_frame(client_socket, asdu3, "总召激活终止")
        self.total_interrogation_done.set()

    def handle_yk_select(self, client_socket: socket.socket, data: bytes):
        # 传输原因
        cot_activation_byte = IEC104Const.COT_ACTIVATION.to_bytes(length=1, byteorder="little")
        # 1. 激活确认报文
        asdu = data[6:8] + cot_activation_byte + data[9:]
        # 解析COA
        coa = int.from_bytes(data[10:12], byteorder='little')
        self.send_i_frame(client_socket, asdu, f"遥控选择(COA={coa})，激活确认")

    def handle_yk_exec(self, client_socket: socket.socket, data: bytes):
        # 提取遥信点位地址
        ioa_byte = data[12:15]
        ioa_value = int.from_bytes(ioa_byte, byteorder="little")
        # 提取遥信值
        yx_value = data[15]
        # 解析COA
        coa = int.from_bytes(data[10:12], byteorder='little')
        # 传输原因
        cot_activation_byte = IEC104Const.COT_ACTIVATION.to_bytes(length=1, byteorder="little")
        cot_termination_byte = IEC104Const.COT_ACTIVATION_TERMINATION.to_bytes(length=1, byteorder="little")

        # 1. 激活确认报文
        asdu = data[6:8] + cot_activation_byte + data[9:]
        self.send_i_frame(client_socket, asdu, f"遥控激活确认(COA={coa}, IOA={ioa_value}, 值={yx_value})")

        # 2. 激活终止报文
        asdu2 = data[6:8] + cot_termination_byte + data[9:]
        self.send_i_frame(client_socket, asdu2, f"遥控激活终止(COA={coa}, IOA={ioa_value}, 值={yx_value})")

        # 3. 发送遥信点位（反馈遥控结果）
        self.send_yx(yx_value, ioa_value, coa)

    def handle_float_yt_select(self, client_socket: socket.socket, data: bytes):
        # 解析COA
        coa = int.from_bytes(data[10:12], byteorder='little')
        # 传输原因
        cot_activation_byte = IEC104Const.COT_ACTIVATION.to_bytes(length=1, byteorder="little")
        # 1. 激活确认报文
        asdu = data[6:8] + cot_activation_byte + data[9:]
        self.send_i_frame(client_socket, asdu, f"浮点遥调选择(COA={coa})，激活确认")

    def handle_float_yt_exec(self, client_socket: socket.socket, data: bytes):
        # 解析COA
        coa = int.from_bytes(data[10:12], byteorder='little')
        # 提取遥调点位
        ioa_byte = data[12:15]
        ioa_value = int.from_bytes(ioa_byte, byteorder="little")
        # 提取浮点值
        float_bytes = data[15:20]
        float_value = struct.unpack("<f B", float_bytes)[0]

        # 更新设备功率（仅PCS(IOA=1)/逆变器(IOA=2)，统一COA=1）
        if coa == 1 and ioa_value in (1, 2):
            device_state.update_device_power(coa, ioa_value, float_value)
            # 获取更新后的电表功率(IOA=3)
            meter_power = device_state.get_device_power(1, 3)
            logger.info(f"更新设备功率 - COA={coa} IOA={ioa_value}: {float_value}, 电表功率(IOA=3)自动更新为: {meter_power}")

        # 传输原因
        cot_activation_byte = IEC104Const.COT_ACTIVATION.to_bytes(length=1, byteorder="little")
        cot_termination_byte = IEC104Const.COT_ACTIVATION_TERMINATION.to_bytes(length=1, byteorder="little")

        # 1. 激活确认报文
        asdu = data[6:8] + cot_activation_byte + data[9:]
        self.send_i_frame(client_socket, asdu, f"短浮点遥调激活确认(COA={coa}, IOA={ioa_value}, 值={float_value})")

        # 2. 激活终止报文
        asdu2 = data[6:8] + cot_termination_byte + data[9:]
        self.send_i_frame(client_socket, asdu2, f"短浮点遥调激活终止(COA={coa}, IOA={ioa_value}, 值={float_value})")

        # 3. 上报浮点遥测值（反馈遥调结果）
        # 发送当前设备的最新值
        if coa == 1 and ioa_value in (1, 2):
            current_value = device_state.get_device_power(coa, ioa_value)
            self.send_yc_float_message(client_socket, current_value, ioa_value, coa)
            # 同时上报电表的最新值(IOA=3)
            meter_power = device_state.get_device_power(1, 3)
            self.send_yc_float_message(client_socket, meter_power, 3, 1)
        else:
            self.send_yc_float(float_value, ioa_value, coa)

    def handle_scaled_yt_select(self, client_socket: socket.socket, data: bytes):
        # 解析COA
        coa = int.from_bytes(data[10:12], byteorder='little')
        # 传输原因
        cot_activation_byte = IEC104Const.COT_ACTIVATION.to_bytes(length=1, byteorder="little")
        # 1. 激活确认报文
        asdu = data[6:8] + cot_activation_byte + data[9:]
        self.send_i_frame(client_socket, asdu, f"标度化遥调选择(COA={coa})，激活确认")

    def handle_scaled_yt_exec(self, client_socket: socket.socket, data: bytes):
        # 解析COA
        coa = int.from_bytes(data[10:12], byteorder='little')
        # 提取遥调点位
        ioa_byte = data[12:15]
        ioa_value = int.from_bytes(ioa_byte, byteorder="little")
        # 提取标度化值
        scaled_bytes = data[15:18]
        scaled_value = int.from_bytes(scaled_bytes, byteorder="little")
        # 传输原因
        cot_activation_byte = IEC104Const.COT_ACTIVATION.to_bytes(length=1, byteorder="little")
        cot_termination_byte = IEC104Const.COT_ACTIVATION_TERMINATION.to_bytes(length=1, byteorder="little")

        # 1. 激活确认报文
        asdu = data[6:8] + cot_activation_byte + data[9:]
        self.send_i_frame(client_socket, asdu, f"标度化遥调激活确认(COA={coa}, IOA={ioa_value}, 值={scaled_value})")

        # 2. 激活终止报文
        asdu2 = data[6:8] + cot_termination_byte + data[9:]
        self.send_i_frame(client_socket, asdu2, f"标度化遥调激活终止(COA={coa}, IOA={ioa_value}, 值={scaled_value})")

        # 3. 上报标度化值（反馈遥调结果）
        self.send_yc_scaled_message(client_socket, scaled_value, ioa_value, coa)


    def handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        try:
            client_socket.settimeout(IEC104Config.CLIENT_TIMEOUT)
            self.total_interrogation_done.clear()
            # 重置设备状态
            device_state.reset_all()

            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    logger.info(f"客户端 {client_address} 断开")
                    break

                hex_str = '-'.join([f"{b:02X}" for b in data])
                logger.info(f"收到 {client_address} 报文：{hex_str}")
                self.process_message(client_socket, data, client_address)

        except socket.timeout:
            logger.warning(f"客户端 {client_address} 超时")
        except socket.error as e:
            logger.error(f"客户端 {client_address} 异常：{e}", exc_info=True)
        finally:
            with self.client_lock:
                if client_address in self.client_sockets:
                    del self.client_sockets[client_address]
            client_socket.close()
            logger.info(f"客户端 {client_address} 连接关闭，当前连接数：{len(self.client_sockets)}")

    def stop_server(self):
        self.running = False
        logger.info("关闭服务器...")

        with self.client_lock:
            for addr, sock in self.client_sockets.items():
                try:
                    sock.close()
                    logger.info(f"关闭客户端 {addr}")
                except Exception as e:
                    logger.error(f"关闭客户端 {addr} 失败：{e}")
            self.client_sockets.clear()

        if self.server_socket:
            self.server_socket.close()
            logger.info("服务器套接字关闭")

        logger.info("104服务器已停止")


# ---------------------- 调用示例 ----------------------
if __name__ == "__main__":
    server = IEC104Server()
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()

    print("等待服务器启动...")
    if not server.server_started.wait(timeout=10.0):
        print("❌ 服务器启动超时！")
        server.stop_server()
        exit(1)
    print("✅ 服务器启动完成，开始等待客户端连接+总召完成...")
    print("📌 模拟设备信息：")
    print("   - 统一COA=1")
    print("   - PCS: IOA=1 (功率)")
    print("   - 逆变器: IOA=2 (功率)")
    print("   - 电表: IOA=3 (功率，自动计算=PCS+逆变器)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 用户终止程序，关闭服务器...")
        server.stop_server()