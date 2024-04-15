#导入Pin模块
from machine import Pin, PWM
import dht
import time
from machine import Timer
import network
from simple import MQTTClient
import utime
import ujson
from fall_detection import FallDetection
import network
import urequests
import json

#路由器WIFI账号和密码
ssid="666666"
password="xiyangyuhai99"
#ssid="CMCC-fDb7"
#password="r8wk9c9k"
#ssid="AYNU2"
#password="aynu2955552"
# MQTT服务器信息
#MQTT_BROKER = 'broker.emqx.io'
MQTT_BROKER = '10.20.108.66'
MQTT_PORT = 1883
MQTT_USER = 'mqtt_username'
MQTT_PASSWORD = 'mqtt_password'
# 用于上报实时数据
MQTT_TOPIC = 'esp32/report/data'
# 手动告警
MANUAL_ALARM_MQTT_TOPIC = 'esp32/report/manual/alarm'
# 自动告警
AUTOMATIC_ALARM_MQTT_TOPIC = 'esp32/report/automatic/alarm'

# 百度地图API参数
BAIDU_API_URL = 'http://api.map.baidu.com/location/ip'
BAIDU_API_KEY = 'aujGhARF3F8jw5c4p7nViTcC7voXmwd3'

fall_detection = FallDetection()

# 定义DHT11控制对象
dht11=dht.DHT11(Pin(13))
# 定义按键外部中断，用于发生告警
button = Pin(14, Pin.IN, Pin.PULL_UP)  # 按键连接到ESP32的IO引脚14接k1
buzzer = PWM(Pin(32))  # 蜂鸣器连接到ESP32,32接beep丰凝汽

buzzer.freq(1000)  # 设置蜂鸣器的频率为1000Hz
buzzer.duty(0)  # 初始时将蜂鸣器的占空比设置为0，即静音状态

is_muted = True  # 初始时设置为静音状态
# key1外部中断函数，用于发生/解除告警
def button_pressed(p):
    global is_muted
    if is_muted:
        buzzer.duty(512)  # 当按键按下时，将蜂鸣器的占空比设置为50%，发出声音
        is_muted = False
        print("告警发生，老人疑似发生跌倒！！！")
        send_alarm_mqtt(mqtt_client,True)
    else:
        buzzer.duty(0)  # 当再次按下按键时，将蜂鸣器的占空比设置为0，静音
        is_muted = True
        print("告警解除！！！")
        send_alarm_mqtt(mqtt_client,False)
# 读取 JSON 文件
# 读取 JSON 文件
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = ujson.load(file)
            return data
    except OSError:
        print('Error: Failed to read JSON file')
        return None
#WIFI连接
def wifi_connect():
    wlan=network.WLAN(network.STA_IF)  #STA模式
    wlan.active(True)  #激活
    wlan.disconnect()
    print(wlan.scan())
    start_time=time.time()  #记录时间做超时判断
    
    if not wlan.isconnected():
        print("conneting to network...")
        wlan.connect(ssid,password)  #输入WIFI账号和密码
        i = 1
        while not wlan.isconnected():
            print("正在链接{}...{}".format(ssid,i))
            i += 1
            time.sleep(1)

    print("network information:", wlan.ifconfig())
    return True

# 获取当前定位信息
def get_location():
    response = urequests.get(BAIDU_API_URL + '?ak=' + BAIDU_API_KEY)
    data = json.loads(response.text)
    if data['status'] == 0:
        lat = data['content']['point']['y']
        lng = data['content']['point']['x']
        city = data['content']['address_detail']['city']
        province = data['content']['address_detail']['province']
        address = data['content']['address']
        detailed_address = data['address']
        #print(city,province,address,detailed_address)
        print('Latitude:', lat)
        print('Longitude:', lng)
        #print("address":data['content'][])
        #return {"latitude":lat,"longitude":lng,"city":city,"province":province,"address":address}
        return {"latitude":lat,"longitude":lng}
    else:
        print('Failed to get location')
# 连接MQTT服务器
mqtt_client = None

def create_mqtt_client():
    global mqtt_client

    try:
        mqtt_client = MQTTClient('esp32', MQTT_BROKER, MQTT_PORT)
        mqtt_client.connect()
        print('MQTT已连接')
        return mqtt_client
    except Exception as e:
        print('MQTT连接失败:', e)
        return None

# 上报数据到MQTT服务器
def report_data(t):
    global mqtt_client
    client = mqtt_client
    data=merge_data()
    payload = ujson.dumps(data)
    client.publish(MQTT_TOPIC, payload)
    print('已上报数据:', payload)
# 告警发生时拿到老人当时定位和当前上报数据发给服务端，让服务端发送告警邮件
def send_alarm_mqtt(client,is_triggered,data_dict={}):
    # 获取当前时间的时间戳
    current_timestamp = utime.time()
    # 将时间戳转换为日期和时间
    current_time = utime.localtime(current_timestamp)
    # 提取日期和时间部分
    year, month, day, hour, minute, second, _, _ = current_time
    # 构建时间字符串
    time_string = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, day, hour, minute, second)
    data_dict = {"alert_time":time_string}
    if is_triggered:
        # 告警发生
        print("发送告警发生")
        data_dict['action'] = is_triggered
        payload = ujson.dumps(data_dict)
        client.publish(MANUAL_ALARM_MQTT_TOPIC, payload)  # 发布告警消息到指定的主题
    else:
        data_dict['action'] = is_triggered
        payload = ujson.dumps(data_dict)
        client.publish(MANUAL_ALARM_MQTT_TOPIC, payload)  # 发布告警解除消息到指定的主题
        print("发送告警解除")

# 获取温度和湿度数据
def get_temperature_humidity():
    time.sleep(2)
    dht11.measure()  #调用DHT类库中测量数据的函数
    temperature = dht11.temperature()
    if temperature==None:
        print("DHT11传感器检测失败！")
        return False
    humidity = dht11.humidity()
    time.sleep(2)
    return {'environment_temperature':temperature,"humidity":humidity}
# 整理各个传感器的数据，合并后用于上报
def merge_data():
     # 获取当前时间的时间戳
    current_timestamp = utime.time()
    # 将时间戳转换为日期和时间
    current_time = utime.localtime(current_timestamp)
    # 提取日期和时间部分
    year, month, day, hour, minute, second, _, _ = current_time
    # 构建时间字符串
    time_string = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(year, month, day, hour, minute, second)
    data_dict = {"report_time":time_string}
    # 整理温度湿度数据
    temp_hum_dict = get_temperature_humidity()
    data_dict.update(temp_hum_dict)
    #整理加速度数据
    data_dict.update(fall_detection.sensor_data())
    # 整理经纬度数据
    #location_data = get_location()
    #data_dict.update(location_data)
    # 整理心率，血氧，体温数据
    heart_data = read_json_file('data.json')
    data_dict.update(heart_data)
    #print(data_dict)
    return data_dict
    
    

#程序入口
if __name__=="__main__":
    time.sleep(2)  # Initial delay for sensor stabilization
    wifi_connect()
    create_mqtt_client()
    button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)
    tim = Timer(0)
    tim.init(period=3000, mode=Timer.PERIODIC, callback=report_data)
