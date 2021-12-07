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
        spectrum = 20 if spectrum is "red-blue" else 10
        lux = (sensor_data[0]<<8 | sensor_data[1]) / 1.2
        ppfd = lux * 20 / spectrum
        return ppfd

    async def start_log(self, update_interval=60):

        log = cloud.Iot("ph")

        while True:
            self.update_time()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "ppfd": self.measure_ppfd(self.get_hi_res_value())})
            await uasyncio.sleep(update_interval)