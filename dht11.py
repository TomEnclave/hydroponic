import uasyncio
import dht
import machine
import timer
import cloud
import db
import screen
from debug import log
debug = True

class Dht11(timer.Automation):
    
    def __init__(self, dht_pin = 27):
        super().__init__()
        self.dht_pin = dht.DHT11(machine.Pin(dht_pin))
    
    def measure_dht(self):
        self.dht_pin.measure()
        temperature = self.dht_pin.temperature()
        humidity = self.dht_pin.humidity()

        log("----------------DHT11 Sensor---------------", debug)
        log("Air temperature: {0}  | Air humidity: {1}".format(temperature, humidity), debug)
        log("-------------------------------------------", debug)

        return temperature, humidity
        
    async def start_log(self, update_interval=60):
        
        id = 'air'

        log = cloud.Iot(id)
        local = db.Database(id)
        display = screen.Display(id)

        while True:
            self.update_time()
            room_temperature, room_humidity = self.measure_dht()

            data = {"year": self.current_year, 
                    "month": self.current_month, 
                    "day": self.current_day,
                    "hour": self.current_hour, 
                    "minute": self.current_minute, 
                    "air temperature": room_temperature, 
                    "air humidity": room_humidity}

            try:
                log.send(data)
                amount_to_keep_locally = 5
            except:
                amount_to_keep_locally = 50

            local.save_data(data, amount_to_keep_locally)

            display.refresh()

            await uasyncio.sleep(update_interval)