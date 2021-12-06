import temperature
import uasyncio
import cloud
import config_ec

class Ec(temperature.Temp):
      
    import machine
    
    def __init__(self, thermistor = machine.ADC(machine.Pin(config_ec.pin_thermistor)), 
                    ec_pin = machine.ADC(machine.Pin(config_ec.pin_ec_read)), 
                    ec_ground = machine.Pin(config_ec.pin_ec_ground, machine.Pin.OUT), 
                    ec_power = machine.Pin(config_ec.pin_ec_power, machine.Pin.OUT), 
                    ec_resistor = config_ec.resistor, 
                    pin_resistance = config_ec.pin_resistance, 
                    pin_voltage = config_ec.pin_voltage, 
                    calibration_ec = config_ec.calibration_ec, 
                    temperature_coeficient = config_ec.temperature_coeficient, 
                    ppm_conversion = config_ec.ppm_conversion, 
                    cell_constant = config_ec.K):
        super().__init__()
        self.thermistor = thermistor
        self.ec_pin = ec_pin
        self.ec_ground = ec_ground
        self.ec_power = ec_power

        self.resistance = ec_resistor + pin_resistance
        self.pin_voltage = pin_voltage
        self.pin_resistance = pin_resistance
        self.calibration_ec = calibration_ec
        self.temperature_coeficient = temperature_coeficient
        self.ppm_conversion = ppm_conversion
        self.cell_constant = cell_constant
    
    #Below are micropython viper functions, accessing gpio's through register, to bypass speed limitations of micropython
    #GPIO's are hardcoded for now, ec_power set to GPIO 26
    @micropython.viper
    def quick_gpio_set(self, value:int, mask:int):
        GPIO_OUT = ptr32(0x3FF44004) # Esp32 GPIO 0-31 Set register
        GPIO_OUT[0] = (GPIO_OUT[0] & mask) | value

    @micropython.viper
    def quick_gpio_clear(self, value:int, mask:int):
        GPIO_OUT = ptr32(0x3FF4400C) # Esp32 GPIO 0-31 Clear register
        GPIO_OUT[0] = (GPIO_OUT[0] & mask) | value
    
    @micropython.viper
    def quick_measure(self):
        self.quick_gpio_set(0b00000100000000000000000000000000,
         0b11111111111111111111111111111111)

        raw_reading = self.ec_pin.read()
        raw_reading = self.ec_pin.read()

        self.quick_gpio_clear(0b00000100000000000000000000000000,
         0b11111111111111111111111111111111)

        return raw_reading

    async def measure_ec(self):

        raw_reading = self.quick_measure()

        print("--------read every 5 sec--------")
        print("ADC raw read (0 - 1024) (0 - 3.3v):")
        print(raw_reading)

        measured_temperature = self.measure_temperature()

        voltage_drop = (self.pin_voltage * raw_reading) / self.bit_width
        resistance = (voltage_drop * self.resistance) / (self.pin_voltage - voltage_drop) - self.pin_resistance
        
        ec = 1000 / (resistance * self.cell_constant)
        ec25 = ec / ( 1 + self.temperature_coeficient * (measured_temperature - 25.0))
        ppm = ec25 * (self.ppm_conversion * 1000)

        print("measured_temperature:")
        print(measured_temperature)
        print("ppm:")
        print(ppm)
        print("ec adjusted for temperature:")
        print(ec25)
        print("ec NOT adjusted for temperature:")
        print(ec)

        return measured_temperature, ppm, ec25, ec

    async def start_log(self, update_interval=60):

        log = cloud.Iot("ppm")

        import machine

        while True:
            self.calibrate_adc(attenuation = machine.ADC.ATTN_11DB, bit_width = machine.ADC.WIDTH_10BIT)
            self.update_time()
            measured_temperature, ppm, ec25, ec = await self.measure_ec()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "temperature": measured_temperature, "ppm": ppm, "ec": ec25, "ec_uncompensated": ec})
            await uasyncio.sleep(update_interval)