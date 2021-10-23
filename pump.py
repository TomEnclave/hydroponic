import timer
import uasyncio
import cloud

class Pump(timer.Automation):

    async def start(self, minutes_to_work, minutes_to_rest):

        log = cloud.Iot("pump")
        
        seconds_to_work = minutes_to_work# * 60
        seconds_to_rest = minutes_to_rest# * 60

        while True:

            self.update_time()

            self.device.on()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "status": "ON"})
            await uasyncio.sleep(seconds_to_work)

            self.device.off()
            log.send({"hour": self.current_hour, "minute": self.current_minute, "status": "OFF"})
            await uasyncio.sleep(seconds_to_rest)

