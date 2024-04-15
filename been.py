import network
import urequests
import json

# Wi-Fi连接参数
#WIFI_SSID = 'Xiaomi_0E0C'
#WIFI_PASSWORD = 'hlf13045'
WIFI_SSID = 'AYNU2'
WIFI_PASSWORD = 'aynu2955552'
# 百度地图API参数
BAIDU_API_URL = 'http://api.map.baidu.com/location/ip'
BAIDU_API_KEY = 'lHGem8BSeNkr84OOOaGDB0vdiHHpqGi8'

# 连接Wi-Fi
def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print('Connecting to Wi-Fi...')
        wifi.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wifi.isconnected():
            pass
    print('Wi-Fi connected')
    print('IP address:', wifi.ifconfig()[0])

# 获取当前定位信息
def get_location():
    response = urequests.get(BAIDU_API_URL + '?ak=' + BAIDU_API_KEY)
    data = json.loads(response.text)
    if data['status'] == 0:
        print(data)
        lat = data['content']['point']['y']
        lng = data['content']['point']['x']
        city = data['content']['address_detail']['city']
        province = data['content']['address_detail']['province']
        address = data['content']['address']
        detailed_address = data['address']
        print(city,province,address,detailed_address)
        print('Latitude:', lat)
        print('Longitude:', lng)
    else:
        print('Failed to get location')

# 主程序
def main():
    connect_wifi()
    get_location()

# 执行主程序
main()