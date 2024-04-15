from micropyGPS import MicropyGPS
import machine

uart = machine.UART(2, baudrate=9600, tx=16, rx=17)  # 根据您的硬件设置选择正确的UART编号和引脚
gps = MicropyGPS()

START_MARKER = '$'
END_MARKER = '\r\n'

while True:
    if uart.any():
        data = uart.readline()
        try:
            data = data.decode('utf-8').strip()
            print(data)
            
            if len(data) > 0 and data.startswith(START_MARKER) and data.endswith(END_MARKER):
                gps.update(data)
            latitude = gps.latitude_string()
            longitude = gps.longitude_string()
            speed = gps.speed_string('kph')
            compass = gps.compass_direction()
            date = gps.date_string('long')
                
            print(latitude)
            print(longitude)
            print(speed)
            print(compass)
            print("时间:",date)
            
        except UnicodeError as e:
            print("Unicode Error:", e)