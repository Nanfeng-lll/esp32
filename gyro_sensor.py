from machine import Pin
import utime
import math
import mpu6050

class GyroSensor:
    def __init__(self):
        self.mpu = mpu6050.MPU6050()
        self.mpu.setSampleRate(200)  # 设置采样率
        self.mpu.setGResolution(2)  # 设置g分辨率
        self.gxoffset = 0.07
        self.gyoffset = -0.04
        # 设置跌倒判断的阈值
        self.fall_threshold = 45

    def averageMPU(self, count, timing_ms):
        gx = 0
        gy = 0
        gz = 0
        for i in range(count):
            g = self.mpu.readData()
            gx = gx + g.Gx - self.gxoffset
            gy = gy + g.Gy - self.gyoffset
            gz = gz + g.Gz
            utime.sleep_ms(timing_ms)
        return gx / count, gy / count, gz / count

    def getAngles(self):
        gx, gy, gz = self.averageMPU(20, 5)
        vdim = math.sqrt(gx * gx + gy * gy + gz * gz)
        rad2degree = 180 / math.pi
        angleX = rad2degree * math.asin(gx / vdim)
        angleY = rad2degree * math.asin(gy / vdim)
        angleZ = rad2degree * math.asin(gz / vdim)
        return angleX, angleY, angleZ
    
    def isFallen(self):
        angleX, angleY, angleZ = self.getAngles()
        print(abs(angleX))
        print(abs(angleY))
        if abs(angleX) > self.fall_threshold or abs(angleY) > self.fall_threshold:
            return True
        else:
            return False
        
if __name__ == "__main__":

    # 创建陀螺仪对象
    gyro = GyroSensor()

    while True:
        if gyro.isFallen():
            print("跌倒！")
        else:
            print("正常")

        utime.sleep(1)

