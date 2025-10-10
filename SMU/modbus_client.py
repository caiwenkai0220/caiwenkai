from itertools import count

from pymodbus.client import ModbusTcpClient

# TCP连接示例
client = ModbusTcpClient('127.0.0.1',port=2405)
client.connect()

# # 读取保持寄存器
# result = client.read_holding_registers(address=12345,count=4,device_id=1)
# print(result.registers)
# # 写单个保持寄存器
# client.write_register(0,111,device_id=1)
# 写多个保持寄存器
# values = list(range(1,101))
# client.write_registers(address=0,values=values,device_id=1)

# 读取线圈值
# result1 = client.read_coils(address=1,count=4,device_id=2)
# print(result1.bits)
# 写单个线圈
# client.write_coil(address=0,value=True,device_id=2)
# 写多个线圈
values = [True,True,True,True,True,True,True,True,True,True,]
client.write_coils(address=0,values=values,device_id=2)


