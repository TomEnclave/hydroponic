import machine
import uasyncio
import cloud
import temperature
import db
import screen
import config_ec
from debug import log
debug = True

class Ec(temperature.Temp):
    
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

        log("-----------------EC Sensor-----------------", debug)
        log("ADC raw read: {0} | Max ADC (bit width): {1} | Attenuation: {2}".format(raw_reading, self.bit_width, self.attenuation), debug)

        measured_temperature = self.measure_temperature()

        voltage_drop = (self.pin_voltage * raw_reading) / self.bit_width
        resistance = (voltage_drop * self.resistance) / (self.pin_voltage - voltage_drop) - self.pin_resistance
        
        ec = 1000 / (resistance * self.cell_constant)
        ec25 = ec / ( 1 + self.temperature_coeficient * (measured_temperature - 25.0))
        ppm = ec25 * (self.ppm_conversion * 1000)
        
        log("measured_temperature: {0} | ppm: {1} | ec adjusted for temperature: {2} | NOT adjusted: {3}".format(measured_temperature, ppm, ec25, ec), debug)
        log("-------------------------------------------", debug)

        return measured_temperature, ppm, ec25, ec

    async def start_log(self, update_interval=60):

        id = 'ec'

        log = cloud.Iot(id)
        local = db.Database(id)
        display = screen.Display(id)

        while True:
            self.calibrate_adc(attenuation = machine.ADC.ATTN_11DB, bit_width = machine.ADC.WIDTH_10BIT)
            self.update_time()
            measured_temperature, ppm, ec25, ec = await self.measure_ec()

            data = {"year": self.current_year, 
                    "month": self.current_month, 
                    "day": self.current_day, 
                    "hour": self.current_hour, 
                    "minute": self.current_minute, 
                    "temperature": measured_temperature, 
                    "ppm": ppm, 
                    "ec": ec25, 
                    "ec_uncompensated": ec}

            try:
                log.send(data)
                amount_to_keep_locally = 5
            except:
                amount_to_keep_locally = 10

            local.save_data(data, amount_to_keep_locally)

            display.refresh()

            await uasyncio.sleep(update_interval)