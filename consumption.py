import machine
import uasyncio
import timer
import cloud
import db
import screen
from debug import log
debug = True

class Consumption(timer.Automation):
    
    def __init__(self, consumption_pin = machine.ADC(machine.Pin(33), measured_device_voltage = 12, acs712_amps = 20)):
        super().__init__()
        self.power_meter = consumption_pin
        self.measured_device_voltage = 12
        self.acs712_vcc = 5
        self.default_output_voltage_before_divider = self.acs712_vcc / 2
        self.voltage_divider_r1 = 10000
        self.voltage_divider_r2 = 15000
        self.default_output_voltage = (self.default_output_voltage_before_divider * self.voltage_divider_r2) / (self.voltage_divider_r1 + self.voltage_divider_r2)
        self.voltage_divider_coefficient = 1 / (self.default_output_voltage_before_divider / self.default_output_voltage)
        self.acs712_amps = 20
        if self.acs712_amps == 5:
            self.amp_rate = 0.066 * self.voltage_divider_coefficient
        elif self.acs712_amps == 20:
            self.amp_rate = 0.1 * self.voltage_divider_coefficient
        elif self.acs712_amps == 30:
            self.amp_rate = 0.185 * self.voltage_divider_coefficient
        else:
            self.amp_rate = 0.1 * self.voltage_divider_coefficient

    def calibrate_adc(self, attenuation = machine.ADC.ATTN_11DB, bit_width = machine.ADC.WIDTH_12BIT):
        self.power_meter.atten(attenuation)
        self.power_meter.width(bit_width)
        #ADC.ATTN_0DB: 0dB attenuation, gives a maximum input voltage of 1.00v - this is the default configuration
        #ADC.ATTN_2_5DB: 2.5dB attenuation, gives a maximum input voltage of approximately 1.34v
        #ADC.ATTN_6DB: 6dB attenuation, gives a maximum input voltage of approximately 2.00v
        #ADC.ATTN_11DB: 11dB attenuation, gives a maximum input voltage of approximately 3.6v
        if attenuation == 0:
            self.attenuation = 1.00
        if attenuation == 1:
            self.attenuation = 1.34
        if attenuation == 2:
            self.attenuation = 2.00
        if attenuation == 3:
            self.attenuation = 3.6
        #ADC.WIDTH_9BIT: 512 values
        #ADC.WIDTH_10BIT: 1024
        #ADC.WIDTH_11BIT: 2048
        #ADC.WIDTH_12BIT: 4096 - this is the default configuration
        if bit_width == 0:
            self.bit_width = 512
        if bit_width == 1:
            self.bit_width = 1024
        if bit_width == 2:
            self.bit_width = 2048
        if bit_width == 3:
            self.bit_width = 4096
    
    def measure_consumption(self):
        read_value = self.power_meter.read()
        #divider = 0
        #for x in range(10):
        #    read_value += self.power_meter.read()
        #    divider += 1
        #read_value = read_value / divider
        #total_voltage = (read_value / self.bit_width) * self.measured_device_voltage
        total_voltage = (self.attenuation / self.bit_width) * read_value
        load_voltage = total_voltage - self.default_output_voltage
        load_voltage = load_voltage * -1 # for some reason voltage drops instead of rising, so it needs to be inverted
        device_current = load_voltage / self.amp_rate
        device_consumption = device_current * self.measured_device_voltage

        log("------------------Power Consumption-------------------", debug)
        log("ADC read value: {0} | Total Voltage: {1} | Load Voltage: {2}".format(read_value, total_voltage, load_voltage), debug)
        log("Device Current: {0} | Consumption: {1}".format(device_current, device_consumption), debug)
        log("------------------------------------------------------", debug)
        
        return device_consumption
        
    async def start_log(self, update_interval=60):
        
        id = 'power'

        log = cloud.Iot(id)
        local = db.Database(id)
        display = screen.Display(id)

        while True:
            self.calibrate_adc(attenuation = machine.ADC.ATTN_11DB, bit_width = machine.ADC.WIDTH_12BIT)
            self.update_time()

            data = {"year": self.current_year, 
                    "month": self.current_month, 
                    "day": self.current_day,
                    "hour": self.current_hour, 
                    "minute": self.current_minute, 
                    "consumption": self.measure_consumption()}

            try:
                log.send(data)
                amount_to_keep_locally = 5
            except:
                amount_to_keep_locally = 50

            local.save_data(data, amount_to_keep_locally)

            display.refresh()

            await uasyncio.sleep(update_interval)