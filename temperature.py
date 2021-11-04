import timer
import uasyncio
import cloud

class Temp(timer.Automation):
      
    import machine
    
    def __init__(self, thermistor = machine.ADC(machine.Pin(36))):
        super().__init__()
        self.thermistor = thermistor
        #self.device = 0

    def calibrate_adc(self, attenuation = machine.ADC.ATTN_11DB, bit_width = machine.ADC.WIDTH_10BIT):
        self.thermistor.atten(attenuation)
        self.thermistor.width(bit_width)
        #ADC.ATTN_0DB: 0dB attenuation, gives a maximum input voltage of 1.00v - this is the default configuration
        #ADC.ATTN_2_5DB: 2.5dB attenuation, gives a maximum input voltage of approximately 1.34v
        #ADC.ATTN_6DB: 6dB attenuation, gives a maximum input voltage of approximately 2.00v
        #ADC.ATTN_11DB: 11dB attenuation, gives a maximum input voltage of approximately 3.6v
        if attenuation == 0:
            self.attenuation = "1.00"
        if attenuation == 1:
            self.attenuation = "1.34"
        if attenuation == 2:
            self.attenuation = "2.00"
        if attenuation == 3:
            self.attenuation = "3.6"
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
    
    def get_resistance(self, resistor = 10000):
        resistance = resistor / (self.bit_width/self.thermistor.read() - 1)
        return resistance
    
    def measure_temperature(self, nominal_temp = 23, resistance_at_nominal_temp = 8300, beta_from_3000_to_4000 = 3950):
        import math
        steinhart = math.log(self.get_resistance() / resistance_at_nominal_temp) / beta_from_3000_to_4000
        steinhart += 1.0 / (nominal_temp + 273.15)
        temperature = (1.0 / steinhart) - 273.15
        return temperature
        
    async def start_log(self, update_interval=60):

        log = cloud.Iot("temperature")

        while True:
            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "temperature": self.measure_temperature()})
            await uasyncio.sleep(update_interval)