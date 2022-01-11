import timer
import uasyncio
import cloud
from debug import log as console_log
debug = True

class Leds(timer.Automation):

    async def start(self, turn_on_from, turn_on_to):

        log = cloud.Iot("leds")

        while True:
            self.update_time()

            if turn_on_from < self.current_second < turn_on_to:
                self.device.on()
                console_log("-------Leds-------", debug)
                console_log("Leds turned ON", debug)
                console_log("------------------", debug)
                log.send({  "year": self.current_year, 
                            "month": self.current_month, 
                            "day": self.current_day, 
                            "hour": self.current_hour, 
                            "minute": self.current_minute, 
                            "status": "ON"})
            else:
                self.device.off()
                console_log("-------Leds-------", debug)
                console_log("Leds turned OFF", debug)
                console_log("------------------", debug)
                log.send({  "year": self.current_year, 
                            "month": self.current_month, 
                            "day": self.current_day, 
                            "hour": self.current_hour, 
                            "minute": self.current_minute, 
                            "status": "OFF"})

            await uasyncio.sleep(2)#*30)

            