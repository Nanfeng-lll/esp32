from machine import sleep, SoftI2C, Pin, Timer
from utime import ticks_diff, ticks_us
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
from hrcalc import calc_hr_and_spo2
import ssd1306


class HeartRateMonitor:
    def __init__(self):
        self.beats = 0
        self.finger_flag = False
        self.spo2 = 0
        self.temperature = 0
        self.heart_list = []
        self.spo2_list = []
        self.temp_list = []
        self.oled = None
        self.timer = Timer(1)

    def create_oled(self):
        # Create I2C object (drive the screen)
        i2c_oled = SoftI2C(scl=Pin(18), sda=Pin(23))
        oled_width = 128
        oled_height = 64
        self.oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c_oled)

        self.oled.fill(0)
        self.oled.text('Put your finger', 0, 30)
        self.oled.show()

    def display_info(self, t):
        if not self.finger_flag:
            self.heart_list.clear()
            self.spo2_list.clear()
            self.temp_list.clear()
            self.beats = self.spo2 = self.temperature = 0
            self.oled.fill(0)
            self.oled.text('Put your finger', 0, 30)
            self.oled.show()
            return

        bmp_str = f'BPM : {int(self.beats)}'
        spo2_str = f'SPO2: {int(self.spo2)}'
        temp_str = f'TEMP: {int(self.temperature)}'

        if len(self.heart_list) >= 30:
            bmp_str += f' <-- {30 - len(self.heart_list)}'
        elif len(self.spo2_list) >= 10:
            spo2_str += f' <-- {10 - len(self.spo2_list)}'
        elif len(self.temp_list) >= 10:
            temp_str += f' <-- {10 - len(self.temp_list)}'

        self.oled.fill(0)
        self.oled.text(bmp_str, 0, 10)
        self.oled.text(spo2_str, 0, 30)
        self.oled.text(temp_str, 0, 50)
        self.oled.show()

    def get_heart_rate(self):
        i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
        sensor = MAX30102(i2c=i2c)

        if sensor.i2c_address not in i2c.scan():
            print("No sensor found")
            return
        elif not sensor.check_part_id():
            print("Detected I2C device is not MAX30102 or MAX30105")
            return
        else:
            print("Sensor recognized")

        sensor.setup_sensor()
        sensor.set_sample_rate(400)
        sensor.set_fifo_average(8)
        sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)

        t_start = ticks_us()
        max_history = 32
        history = []
        beats_history = []
        beat = False
        red_list = []
        ir_list = []

        while True:
            sensor.check()
            if sensor.available():
                red_reading = sensor.pop_red_from_storage()
                ir_reading = sensor.pop_ir_from_storage()

                if red_reading < 1000:
                    self.finger_flag = False
                    continue
                else:
                    self.finger_flag = True

                if len(self.heart_list) < 30:
                    history.append(red_reading)
                    history = history[-max_history:]
                    minima, maxima = min(history), max(history)
                    threshold_on = (minima + maxima * 3) // 4
                    threshold_off = (minima + maxima) // 2

                    if not beat and red_reading > threshold_on:
                        beat = True
                        t_us = ticks_diff(ticks_us(), t_start)
                        t_s = t_us / 1000000
                        f = 1 / t_s
                        bpm = f * 60
                        if bpm < 500:
                            t_start = ticks_us()
                            beats_history.append(bpm)
                            beats_history = beats_history[-max_history:]
                            self.beats = round(sum(beats_history) / len(beats_history), 2)
                    if beat and red_reading < threshold_off:
                        beat = False
                elif len(self.spo2_list) < 10:
                    red_list.append(red_reading)
                   ir_list.append(ir_reading)
                    if len(red_list) >= 25 and len(ir_list) >= 25:
                        spo2_val = calc_hr_and_spo2(red_list, ir_list)
                        self.spo2 = spo2_val['SpO2']
                        red_list.clear()
                        ir_list.clear()
                elif len(self.temp_list) < 10:
                    self.temp_list.append(red_reading)

                self.display_info(ticks_us())

    def get_temperature(self):
        # Add code to read temperature from a temperature sensor
        pass

    def start(self):
        self.create_oled()
        self.get_heart_rate()
        self.get_temperature()


if __name__ == '__main__':
    hrm = HeartRateMonitor()
    hrm.start()