from machine import Pin, PWM
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)  # 按键连接到ESP32的IO引脚14
buzzer = PWM(Pin(25))  # 蜂鸣器连接到ESP32的IO引脚15

buzzer.freq(1000)  # 设置蜂鸣器的频率为1000Hz
buzzer.duty(0)  # 初始时将蜂鸣器的占空比设置为0，即静音状态

is_muted = True  # 初始时设置为静音状态

def button_pressed(p):
    global is_muted
    if is_muted:
        buzzer.duty(512)  # 当按键按下时，将蜂鸣器的占空比设置为50%，发出声音
        is_muted = False
    else:
        buzzer.duty(0)  # 当再次按下按键时，将蜂鸣器的占空比设置为0，静音
        is_muted = True

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)  # 配置按键的外部中断，下降沿触发

while True:
    time.sleep(1)  # 在主循环中等待，保持程序运行