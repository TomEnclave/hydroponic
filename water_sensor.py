import timer
import uasyncio
import cloud
from debug import log
debug = True

class Waterlevel(timer.Automation):
      
    import machine
    
    def __init__(self, water_level_pin = machine.ADC(machine.Pin(39))):
        super().__init__()
        self.water_level = water_level_pin
        #self.device = 0

    def calibrate_adc(self, attenuation = machine.ADC.ATTN_2_5DB, bit_width = machine.ADC.WIDTH_12BIT):
        self.water_level.atten(attenuation)
        self.water_level.width(bit_width)
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
    
    def measure_water_level(self):
        read_value = self.water_level.read()
        read_value = 1 if read_value is 0 else read_value
        percentage = 100 / (self.bit_width / read_value)
        voltage = read_value/self.bit_width * self.attenuation

        log("---------------------Water Sensor---------------------", debug)
        log("ADC read value: {0} | Percentage: {1} | Voltage: {2}".format(read_value, percentage, voltage), debug)
        log("------------------------------------------------------", debug)

        return percentage
        
    async def start_log(self, update_interval=60):
        import machine

        log = cloud.Iot("water_level")

        while True:
            self.calibrate_adc(attenuation = machine.ADC.ATTN_6DB, bit_width = machine.ADC.WIDTH_12BIT)
            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "water level": self.measure_water_level()})
            await uasyncio.sleep(update_interval)