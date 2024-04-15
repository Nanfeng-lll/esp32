import machine
import re

uart = machine.UART(2, baudrate=9600, tx=17, rx=16)  # 根据您的硬件设置选择正确的UART编号和引脚

while True:
    if uart.any():
        data = uart.readline()
        print(data)
        # 使用with关键字打开文件并追加写入内容
        with open('data.txt', 'a') as file:
            file.write(data)
