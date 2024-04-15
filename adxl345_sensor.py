import machine
import time

# 3.3v
class ADXL345Sensor:
    # 定义ADXL345的I2C地址
    ADXL345_ADDR = 0x53

    # 定义寄存器地址
    POWER_CTL = 0x2D
    DATA_FORMAT = 0x31
    DATAX0 = 0x32
    DATAX1 = 0x33
    DATAY0 = 0x34
    DATAY1 = 0x35
    DATAZ0 = 0x36
    DATAZ1 = 0x37

    def __init__(self, sda_pin=12, scl_pin=27):
        # 初始化软件模拟的I2C总线
        self.i2c = machine.SoftI2C(sda=sda_pin, scl=scl_pin)

        # 配置ADXL345
        self.i2c.writeto(self.ADXL345_ADDR, bytearray([self.POWER_CTL, 0x08]))  # 开启测量模式
        self.i2c.writeto(self.ADXL345_ADDR, bytearray([self.DATA_FORMAT, 0x08]))  # 设置数据格式为全分辨率

    def read_acceleration(self):
        # 读取X轴加速度数据
        data_x0 = self.i2c.readfrom_mem(self.ADXL345_ADDR, self.DATAX0, 1)[0]
        data_x1 = self.i2c.readfrom_mem(self.ADXL345_ADDR, self.DATAX1, 1)[0]
        data_x = (data_x1 << 8) | data_x0

        # 读取Y轴加速度数据
        data_y0 = self.i2c.readfrom_mem(self.ADXL345_ADDR, self.DATAY0, 1)[0]
        data_y1 = self.i2c.readfrom_mem(self.ADXL345_ADDR, self.DATAY1, 1)[0]
        data_y = (data_y1 << 8) | data_y0

        # 读取Z轴加速度数据
        data_z0 = self.i2c.readfrom_mem(self.ADXL345_ADDR, self.DATAZ0, 1)[0]
        data_z1 = self.i2c.readfrom_mem(self.ADXL345_ADDR, self.DATAZ1, 1)[0]
        data_z = (data_z1 << 8) | data_z0

        return {"X": data_x, "Y": data_y, "Z": data_z}
    def is_fallen(self):
        # 读取两个连续时刻的加速度数据
        acceleration1 = self.read_acceleration()
        time.sleep(0.1)  # 等待0.1秒
        acceleration2 = self.read_acceleration()

        # 计算加速度的变化量
        delta_x = abs(acceleration2['X'] - acceleration1['X'])
        delta_y = abs(acceleration2['Y'] - acceleration1['Y'])
        delta_z = abs(acceleration2['Z'] - acceleration1['Z'])
        print(delta_x)
        print(delta_y)
        print(delta_z)

        # 判断是否摔倒
        if delta_x > 200 or delta_y > 200 or delta_z > 200:
            return True
        else:
            return False

if __name__ == "__main__":
    adxl345 = ADXL345Sensor(sda_pin=machine.Pin(12), scl_pin=machine.Pin(27))

    # 检测是否摔倒
    while True:
        # 判断是否摔倒
        if adxl345.is_fallen():
            print("摔倒了！")
        else:
            print("未摔倒！")

        time.sleep(1)  # 每隔1秒检测一次
