import uasyncio
import timer
import cloud
import db
import screen
from debug import log as console_log
debug = True

class Pump(timer.Automation):

    async def start(self, minutes_to_work, minutes_to_rest):

        id = 'pump'

        log = cloud.Iot(id)
        local = db.Database(id)
        display = screen.Display(id)
        
        seconds_to_work = minutes_to_work# * 60
        seconds_to_rest = minutes_to_rest# * 60

        while True:

            self.update_time()

            self.device.on()
            
            data = {    "year": self.current_year, 
                        "month": self.current_month, 
                        "day": self.current_day, 
                        "hour": self.current_hour, 
                        "minute": self.current_minute, 
                        "status": "ON"}
            
            try:
                log.send(data)
                amount_to_keep_locally = 5
            except:
                amount_to_keep_locally = 10

            local.save_data(data, amount_to_keep_locally)

            display.refresh()

            console_log("------Pump------", debug)
            console_log("Pump turned ON", debug)
            console_log("----------------", debug)

            await uasyncio.sleep(seconds_to_work)

            self.device.off()
            
            data = {    "year": self.current_year, 
                        "month": self.current_month, 
                        "day": self.current_day, 
                        "hour": self.current_hour, 
                        "minute": self.current_minute, 
                        "status": "OFF"}
            
            try:
                log.send(data)
                amount_to_keep_locally = 5
            except:
                amount_to_keep_locally = 10

            local.save_data(data, amount_to_keep_locally)

            display.refresh()

            console_log("-----Pump-------", debug)
            console_log("Pump turned OFF", debug)
            console_log("----------------", debug)

            await uasyncio.sleep(seconds_to_rest)