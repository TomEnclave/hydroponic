import timer
import uasyncio
import cloud

class Ppfd(timer.Automation):

    def __init__(self, scl_pin, sda_pin, bh1750_address = 0x23):
        import machine
        self.i2c = machine.I2C(machine.Pin(scl_pin),machine.Pin(sda_pin))
        self.bh1750_address = bh1750_address
        self.i2c.writeto(self.bh1750_address, bytes([0x01])) #Starts the sensor
    
    async def get_hi_res_value(self):
        self.i2c.writeto(self.bh1750_address, bytes([0x20])) #0x21 can be used too, but the result of measure_ppfd function needs to be multiplied by 2
        await uasyncio.sleep_ms(180)
        return self.i2c.readfrom(self.bh1750_address, 2)
    
    async def get_low_res_value(self):
        self.i2c.writeto(self.bh1750_address, bytes([0x10])) #0x11 can be used too, but the result of measure_ppfd function needs to be multiplied by 2
        await uasyncio.sleep_ms(24)
        return self.i2c.readfrom(self.bh1750_address, 2)
    
    async def measure_ppfd(self, sensor_data, spectrum = "red-blue"):
        if spectrum is "red": #650nm
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
        return ppfd

    async def start_log(self, update_interval=60):

        log = cloud.Iot("ppfd")

        while True:
            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "ppfd": self.measure_ppfd(self.get_hi_res_value())})
            await uasyncio.sleep(update_interval)