import timer
import uasyncio
import cloud
from debug import log
debug = True

class WaterTank(timer.Automation):
    
    def __init__(self, water_tank_pin = 12):
        import machine
        super().__init__()
        self.water_level = machine.Pin(water_tank_pin, machine.Pin.IN, machine.Pin.PULL_UP)
    
    def check_water_level(self):
        tank_level_value = self.water_level.value()
        tank_level = "Above level" if tank_level_value is 0 else "Below level"

        log("---------------------Water Tank---------------------", debug)
        log("Water level pin value: {0}".format(tank_level_value), debug)
        log("Water level in the tank: {0}".format(tank_level), debug)
        log("------------------------------------------------------", debug)

        return tank_level
        
    async def start_log(self, update_interval=60):

        log = cloud.Iot("water_tank")

        while True:
            self.update_time()
            log.send({  "year": self.current_year, 
                        "month": self.current_month, 
                        "day": self.current_day, 
                        "hour": self.current_hour, 
                        "minute": self.current_minute, 
                        "water level": self.check_water_level()})
            await uasyncio.sleep(update_interval)