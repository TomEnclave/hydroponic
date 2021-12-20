import timer
import uasyncio
import cloud
import dht
import machine

class Dht11(timer.Automation):
    
    def __init__(self, dht_pin = 5):
        super().__init__()
        self.dht_pin = dht.DHT11(machine.Pin(dht_pin))
        #self.device = 0
    
    def measure_dht(self):
        self.dht_pin.measure()
        temperature = self.dht_pin.temperature()
        humidity = self.dht_pin.humidity()
        return temperature, humidity
        
    async def start_log(self, update_interval=60):

        log = cloud.Iot("room")

        while True:
            self.update_time()
            room_temperature, room_humidity = self.measure_dht()
            print("Room temperature: {0}  | Room humidity: {1}".format(room_temperature, room_humidity))
            print(room_temperature)
            log.send({"hour": self.current_hour, "minute": self.current_minute, "room temperature": room_temperature, "room humidity": room_humidity})
            await uasyncio.sleep(update_interval)