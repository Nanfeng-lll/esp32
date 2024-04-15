import math
import machine
import time
from adxl345_sensor import ADXL345Sensor
from gyro_sensor import GyroSensor

class FallDetection:
    def __init__(self):
        self.accel = ADXL345Sensor(12,27)  # 创建加速计实例
        self.gyro = GyroSensor()  # 创建陀螺仪实例

    def detect_fall(self):
        if self.accel.is_fallen() and self.gyro.isFallen():
            print("摔倒了")
        else:
            print("正常")
        

    def trigger_alarm(self):
        # 触发警报的逻辑
        print("摔倒警报！")
    def sensor_data(self):
        accel_data = self.accel.read_acceleration()
        gyro_x,gyro_y,gyro_z = self.gyro.getAngles()
        gyro_data = {"gx":gyro_x,"gy":gyro_y,"gz":gyro_z}
        accel_data.update(gyro_data)
        print(accel_data)
        return accel_data

if __name__ == "__main__":
    fall_detection = FallDetection()
    fall_detection.sensor_data()
    while True:
        fall_detection.sensor_data()
        #fall_detection.detect_fall()
