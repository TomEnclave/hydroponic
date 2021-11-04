import temperature
import uasyncio
import cloud

class Ec(temperature.Temp):
      
    import machine

    calibration_ec = 1.38 # EC value of Calibration solution is s/cm

    resistor = 1000 # R1
    pin_resistance = 25 # Ra - Pin resistance of ESP32 (compared to 25 in arduino), according to page 43 of esp32_datasheet_en.pdf
    pin_voltage = 3.3 # Esp32 pin voltage is 3.3v / 5v on Arduino UNO

    #The value below will change depending on what chemical solution we are measuring
    #0.019 is generaly considered the standard for plant nutrients [google "Temperature compensation EC" for more info
    temperature_coeficient = 0.019 #this changes depending on what chemical we are measuring

    ppm_conversion = 0.64 # USA = 0.5 / EU = 0.64 / Australia = 0.7

    K = 2.88 # K - Cell Constant - 2.88 for US plugs / 1.76 for EU plugs [Gotten from calibration procedure]
    
    def __init__(self, thermistor = machine.ADC(machine.Pin(36)), ec_pin = machine.ADC(machine.Pin(35)), ec_ground = machine.Pin(19, machine.Pin.OUT), ec_power = machine.Pin(33, machine.Pin.OUT), ec_resistor = resistor, pin_resistance = pin_resistance, pin_voltage = pin_voltage, calibration_ec = calibration_ec, temperature_coeficient = temperature_coeficient, ppm_conversion = ppm_conversion, cell_constant = K):
        #import machine
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

        self.ec_ground.value(0)

    def measure_ec(self):

        self.ec_power.on()
        
        raw_reading = self.ec_pin.read()
        print("raw_reading 1:")
        print(raw_reading)

        self.ec_power.off()

        measured_temperature = self.measure_temperature()

        voltage_drop = (self.pin_voltage * raw_reading) / self.bit_width
        resistance = (voltage_drop * self.resistance) / (self.pin_voltage - voltage_drop) - self.pin_resistance
        
        ec = 1000 / (resistance * self.cell_constant)
        ec25 = ec / ( 1 + self.temperature_coeficient * (measured_temperature - 25.0))
        ppm = ec25 * (self.ppm_conversion * 1000)

        print(measured_temperature)
        print(ppm)
        print(ec25)
        print(ec)

        return measured_temperature, ppm, ec25, ec

    async def start_log(self, update_interval=60):

        log = cloud.Iot("ppm")

        while True:
            self.update_time()
            measured_temperature, ppm, ec25, ec = self.measure_ec()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "temperature": measured_temperature, "ppm": ppm, "ec": ec25, "ec_uncompensated": ec})
            await uasyncio.sleep(update_interval)