import timer
import uasyncio
import cloud
from debug import log
debug = True

class Spectrum(timer.Automation):

    def __init__(self, scl_pin = 17, sda_pin = 16, tcs34725_address = 0x29):
        import machine
        super().__init__()
        self.i2c = machine.SoftI2C(scl = machine.Pin(scl_pin),sda = machine.Pin(sda_pin))
        self.tcs34725_address = tcs34725_address
        self.command_bit = 0b10000000 #Must be added to ANY command, read or write
        self.active_pon_bit = 0b00000001
        self.active_aen_bit = 0b00000010
        self.active_register = 0x00
        self.status_register = 0x13
        self.clear_sum_register = 0x14
        self.red_register = 0x16
        self.green_register = 0x18
        self.blue_register = 0x1a
        self.enable_bit = self.i2c.readfrom_mem(tcs34725_address, self.command_bit | self.active_register, 1)[0]
        self.ready = bool(bin(self.i2c.readfrom_mem(tcs34725_address, self.command_bit | self.status_register, 1)[0] & 0b00000001)) # Checks if last bit is set to 1
        self.sensor_id = hex(self.i2c.readfrom_mem(self.tcs34725_address, self.command_bit | 0x12, 1)[0])

        self.i2c.writeto_mem(self.tcs34725_address, self.active_register, 
                                bytes([self.command_bit | self.enable_bit | self.active_pon_bit])) #Starts the sensor
        uasyncio.sleep_ms(3)
        self.i2c.writeto_mem(self.tcs34725_address, self.active_register, 
                                bytes([self.command_bit | self.enable_bit | self.active_pon_bit | self.active_aen_bit]))
        
        log("Spectrum Sensor ID: {0}".format(self.sensor_id), debug)
    
    async def measure(self):
        while not self.ready:
            uasyncio.sleep_ms(24)

        raw_clear_sum = int.from_bytes(self.i2c.readfrom_mem(self.tcs34725_address, self.command_bit | self.clear_sum_register, 2), "little")
        raw_red = int.from_bytes(self.i2c.readfrom_mem(self.tcs34725_address, self.command_bit | self.red_register, 2), "little")
        raw_green = int.from_bytes(self.i2c.readfrom_mem(self.tcs34725_address, self.command_bit | self.green_register, 2), "little")
        raw_blue = int.from_bytes(self.i2c.readfrom_mem(self.tcs34725_address, self.command_bit | self.blue_register, 2), "little")
        
        #if raw_clear_sum <= 0: # eliminating division by 0
        #    raw_clear_sum = 1
        #    raw_red = 1
        #    raw_green = 1
        #    raw_blue = 1

        rgb_red = raw_red / raw_clear_sum * 255
        rgb_green = raw_green / raw_clear_sum * 255 
        rgb_blue = raw_blue / raw_clear_sum * 255

        x = -0.14282 * raw_red + 1.54924 * raw_green + -0.95641 * raw_blue
        y_lux = -0.32466 * raw_red + 1.57837 * raw_green + -0.73191 * raw_blue
        z = -0.68202 * raw_red + 0.77073 * raw_green +  0.56332 * raw_blue

        chromaticity_coordinates_xc = (x) / (x + y_lux + z)
        chromaticity_coordinates_yc = (y_lux) / (x + y_lux + z)

        mccamys_color_temperature = (chromaticity_coordinates_xc - 0.3320) / (0.1858 - chromaticity_coordinates_yc)

        cct = (449.0 * pow(mccamys_color_temperature, 3)) + (3525.0 * pow(mccamys_color_temperature, 2)) + (6823.3 * mccamys_color_temperature) + 5520.33
        
        log("-----------------TCS34725 Sensor-----------------", debug)
        log("Status Ready: {0}".format(self.ready), debug)
        log("RGB: [{0}; {1}; {2}]".format(rgb_red, rgb_green, rgb_blue), debug)
        log("Raw: [{0}; {1}; {2}] / [{3}]".format(raw_red, raw_green, raw_blue, raw_clear_sum), debug)
        log("Lux: {0}".format(y_lux), debug)
        log("Chromaticity Coords: X {0}; Y {1}".format(chromaticity_coordinates_xc, chromaticity_coordinates_yc), debug)
        log("Color Temperature: Mccamy's {0}; CCT {1}".format(mccamys_color_temperature, cct), debug)
        log("-------------------------------------------------", debug)

        return [rgb_red, rgb_green, rgb_blue], [raw_clear_sum, raw_red, raw_green, raw_blue], y_lux, mccamys_color_temperature, cct

class Ppfd(timer.Automation):

    def __init__(self, scl_pin = 22, sda_pin = 21, bh1750_address = 0x23):
        import machine
        super().__init__()
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.i2c = machine.SoftI2C(scl = machine.Pin(scl_pin),sda = machine.Pin(sda_pin))
        self.bh1750_address = bh1750_address
        self.i2c.writeto(self.bh1750_address, bytes([0x01])) #Starts the sensor
    
    async def get_hi_res_value(self):
        self.i2c.writeto(self.bh1750_address, bytes([0x20])) #0x21 can be used too, but the result of measure_ppfd function needs to be multiplied by 2
        await uasyncio.sleep_ms(120 * 2) #120ms is the documented response time, but needs atleast 2 times more here, otherwise drops "OSError: [Errno 110] ETIMEDOUT" error
        return self.i2c.readfrom(self.bh1750_address, 2)
    
    async def get_low_res_value(self):
        self.i2c.writeto(self.bh1750_address, bytes([0x10])) #0x11 can be used too, but the result of measure_ppfd function needs to be multiplied by 2
        await uasyncio.sleep_ms(24)
        return self.i2c.readfrom(self.bh1750_address, 2)
    
    async def measure_ppfd(self, sensor_data, spectrum = "red-blue"):

        if isinstance(spectrum, list):
            color_red = spectrum[0]
            color_green = spectrum[1]
            color_blue = spectrum[2]
            red_coefficient = color_red * 13.0122950819672
            blue_coefficient = color_blue * 8.65410497981157
            spectrum_coefficient = (red_coefficient + blue_coefficient) / (color_red + color_blue)
            other_spectrum = spectrum_coefficient
        elif spectrum is "red": #650nm
            other_spectrum = 13.0122950819672
        elif spectrum is "blue": #450nm
            other_spectrum = 8.65410497981157
        elif spectrum is "red-blue-white":
            other_spectrum = 38.9265536723164
        else: # day light
            other_spectrum = 43.4782608695652
        """ 
        Spectrum factors:
            43.4782608695652 for Daylight
            28.9136150234742 for Halogen Lamp 3000K
            58.0260303687636 for High CRI LED 6500K
            56.1085972850679 for High CRI LED 4000K
            52.5557011795544 for High CRI LED 3000K
            74.5889387144992 for Low CRI LED 6500K
            62.3559498956159 for Low CRI LED 3500K
            77.079295154185 for HPS 2000K
            55.092987804878 for CMH 3000K
            74.1128205128205 for Fluorescent Lamp 5000K
            13.0122950819672 for Monochromatic Red LED 650 nm
            8.65410497981157 for Monochromatic Blue LED 450 nm
            11.2700369913687 for Red + Blue LED 450+650 nm
            38.9265536723164 for Red + Blue + White LED 450+650nm+3500K
        """
        spectrum = 11.2700369913687 if spectrum is "red-blue" else other_spectrum
        lux = (sensor_data[0]<<8 | sensor_data[1]) / 1.2
        ppfd = (lux / spectrum * 100) / 100 #umol/s/m2
        log("-----------------BH1750 Sensor-----------------", debug)
        log("Lux: {0} | PPFD: {1}".format(lux, ppfd), debug)
        log("-----------------------------------------------", debug)

        return ppfd, lux

    async def start_log(self, update_interval=60):

        log = cloud.Iot("ppfd")
        spectrums = Spectrum(scl_pin=self.scl_pin, sda_pin=self.sda_pin)

        while True:
            rgb, raw, tcs_lux, color_temperature, cct = await spectrums.measure()
            hi_res = await self.get_hi_res_value()
            ppfd, lux = await self.measure_ppfd(hi_res, spectrum = rgb)
            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "ppfd": ppfd, "rgb": rgb, "raw rgb": raw, "lux bh1750": lux,"lux tcs34725": tcs_lux, "color temperature": color_temperature, "cct": cct})
            await uasyncio.sleep(update_interval)