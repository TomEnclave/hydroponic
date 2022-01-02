from time import time
import temperature
import uasyncio
import cloud
from debug import log
debug = True

class Ph(temperature.Temp):
    
    import machine

    def __init__(self, thermistor = machine.ADC(machine.Pin(36)), ph_pin = machine.ADC(machine.Pin(32)), calibrating = False):
        super().__init__()
        self.thermistor = thermistor
        self.ph_pin = ph_pin
        self.calibrating = calibrating

        global _acid_voltage
        global _neutral_voltage
        try:
            with open('ph_data.txt','r') as f:
                neutral_voltage_line = f.readline()
                neutral_voltage_line = neutral_voltage_line.strip('neutral_voltage=')
                _neutral_voltage    = float(neutral_voltage_line)
                acid_voltage_line    = f.readline()
                acid_voltage_line    = acid_voltage_line.strip('acid_voltage=')
                _acid_voltage       = float(acid_voltage_line)
                log("------------------PH Sensor Settings-------------------", debug)
                log("Neutral Voltage: {0} | Acid Voltage: {1}".format(_neutral_voltage, _acid_voltage), debug)
                log("-------------------------------------------------------", debug)
        except :
            print("ph_data.txt error, resetting to default values..")
            self.reset()
            self.__init__()
    
    def calibrate_adc_ph(self, attenuation = machine.ADC.ATTN_6DB, bit_width = machine.ADC.WIDTH_12BIT):
        self.ph_pin.atten(attenuation)
        self.ph_pin.width(bit_width)

        if attenuation == 0:
            self.attenuation = 1.00 #ADC.ATTN_0DB
        if attenuation == 1:
            self.attenuation = 1.34 #ADC.ATTN_2_5DB
        if attenuation == 2:
            self.attenuation = 2.00 #ADC.ATTN_6DB
        if attenuation == 3:
            self.attenuation = 3.6 #ADC.ATTN_11DB

        if bit_width == 0:
            self.bit_width = 512 #ADC.WIDTH_9BIT
        if bit_width == 1:
            self.bit_width = 1024 #ADC.WIDTH_10BIT
        if bit_width == 2:
            self.bit_width = 2048 #ADC.WIDTH_11BIT
        if bit_width == 3:
            self.bit_width = 4096 #ADC.WIDTH_12BIT

    def calibrate_ph(self, voltage):
        if (not self.calibrating):
            return
        print("Calibration started, the voltage is:")
        print(voltage)

        global _acid_voltage
        global _neutral_voltage

        if (voltage > 1.4 and voltage < 1.9):#(voltage>1322 and voltage<1678):
            print("The solution is within [PH 7.0] frame, calibrating..")
            f=open('ph_data.txt','r')

            neutral_voltage_line = f.readline()
            neutral_voltage_line = neutral_voltage_line.strip('neutral_voltage=')
            _neutral_voltage    = float(neutral_voltage_line)

            acid_voltage_line    = f.readline()
            acid_voltage_line    = acid_voltage_line.strip('acid_voltage=')
            _acid_voltage       = float(acid_voltage_line)

            file_lines ='neutral_voltage='+ str(voltage) + '\n'
            file_lines +='acid_voltage='+ str(_acid_voltage) + '\n'

            f=open('ph_data.txt','w')
            f.write(file_lines)
            f.close()

            print ("PH 7.0 calibration completed")

        elif (voltage > 0.4 and voltage < 0.8):#(voltage>1854 and voltage<2210):
            print ("The solution is within [PH 4.0] frame, calibrating..")
            f=open('ph_data.txt','r')

            neutral_voltage_line = f.readline()
            neutral_voltage_line = neutral_voltage_line.strip('neutral_voltage=')
            _neutral_voltage    = float(neutral_voltage_line)

            acid_voltage_line    = f.readline()
            acid_voltage_line    = acid_voltage_line.strip('acid_voltage=')
            _acid_voltage       = float(acid_voltage_line)

            file_lines ='neutral_voltage='+ str(_neutral_voltage) + '\n'
            file_lines +='acid_voltage='+ str(voltage) + '\n'

            f=open('ph_data.txt','w')
            f.write(file_lines)
            f.close()

            print ("PH 4.0 calibration completed")
        else:
            print ("The solution PH value is outside the calibration frame (should be PH ~4 or PH ~7) ")
        
    def measure_voltage(self, adc_value, adc_attenuation=2.0, adc_bit_width=4096):
        measured_voltage = adc_value/adc_bit_width*adc_attenuation
        return measured_voltage

    def measure_ph(self, voltage, temperature=25):
        global _acid_voltage
        global _neutral_voltage

        slope     = (7.0-4.0)/((_neutral_voltage-1.5)/3.0 - (_acid_voltage-1.5)/3.0)
        intercept = 7.0 - slope*(_neutral_voltage-1.5)/3.0
        _ph_value  = slope*(voltage-1.5)/3.0+intercept

        round(_ph_value,2)

        log("------------------PH Sensor-------------------", debug)
        log("PH Value: {0} | Adjusted for temperature: {1}".format(_ph_value, temperature), debug)
        log("----------------------------------------------", debug)

        return _ph_value

    def reset(self):
        _acid_voltage    = 0.5
        _neutral_voltage = 1.5
        try:
            f=open('ph_data.txt','r')

            neutral_voltage_line = f.readline()
            neutral_voltage_line = neutral_voltage_line.strip('neutral_voltage=')
            _neutral_voltage    = float(neutral_voltage_line)

            acid_voltage_line    = f.readline()
            acid_voltage_line    = acid_voltage_line.strip('acid_voltage=')
            _acid_voltage       = float(acid_voltage_line)

            file_lines ='neutral_voltage='+ str(_neutral_voltage) + '\n'
            file_lines +='acid_voltage='+ str(_acid_voltage) + '\n'

            f=open('ph_data.txt','w')
            f.write(file_lines)
            f.close()

            print ("Finished reseting to default parameters")
        except:
            f=open('ph_data.txt','w')

            file_lines   ='neutral_voltage='+ str(_neutral_voltage) + '\n'
            file_lines  +='acid_voltage='+ str(_acid_voltage) + '\n'

            f.write(file_lines)
            f.close()

            print("Finished reseting to default parameters")

    async def start_log(self, update_interval=60):

        log = cloud.Iot("ph")
        import machine
        while True:
            #self.calibrate_adc()
            #measured_temperature = 25; #await self.measure_temperature()
            self.calibrate_adc_ph(attenuation = machine.ADC.ATTN_11DB, bit_width = machine.ADC.WIDTH_12BIT)
            measured_voltage = self.measure_voltage(self.ph_pin.read(), self.attenuation, self.bit_width)
            self.calibrate_ph(measured_voltage)

            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "ph": self.measure_ph(measured_voltage)})#, measured_temperature)})
            await uasyncio.sleep(update_interval)