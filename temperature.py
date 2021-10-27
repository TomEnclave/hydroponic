import uasyncio
import cloud
import timer

class Temp(timer.Automation):
      
    import machine
    
    def __init__(self, device = machine.ADC(machine.Pin(32))):
        super().__init__()
        self.device = device

    def calibrate(self, attenuation = machine.ADC.ATTN_11DB, width = machine.ADC.WIDTH_10BIT):
        self.device.atten(attenuation)
        self.device.width(width)
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
        if width == 0:
            self.width = 512
        if width == 1:
            self.width = 1024
        if width == 2:
            self.width = 2048
        if width == 3:
            self.width = 4096
    
    def get_resistance(self, resistor = 10000):
        print("width")
        print(self.width)
        print(self.device.read())
        resistance = resistor / (self.width/self.device.read() - 1)
        print(resistance) 
        return resistance
    
    
    def measure(self, nominal_temp = 25, resistance_at_nominal_temp = 7000, beta_from_3000_to_4000 = 3950):
        import math
        steinhart = math.log(self.get_resistance() / resistance_at_nominal_temp) / beta_from_3000_to_4000
        steinhart += 1.0 / (nominal_temp + 273.15)
        temperature = (1.0 / steinhart) - 273.15
        return temperature
        

    async def start_log(self, update_interval=60):

        log = cloud.Iot("temperature")

        while True:
            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "temperature": self.measure()})
            await uasyncio.sleep(update_interval)