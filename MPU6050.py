from machine import Pin
import utime
import math
import mpu6050

# 陀螺仪 scl接25，sda接26，vcc接5V
class GyroSensor:
    def __init__(self):
        self.mpu = mpu6050.MPU6050()
        self.mpu.setSampleRate(200)  # 设置采样率
        self.mpu.setGResolution(2)  # 设置g分辨率
        self.gxoffset = 0.07
        self.gyoffset = -0.04

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

# 示例用法
gyro = GyroSensor()

while True:
    angleX, angleY, angleZ = gyro.getAngles()

    # 打印X、Y、Z角度
    print("X角度:", angleX)
    print("Y角度:", angleY)
    print("Z角度:", angleZ)

    utime.sleep(1)