import timer
import uasyncio
import cloud

class Leds(timer.Automation):

    async def start(self, turn_on_from, turn_on_to):

        log = cloud.Iot("leds")

        while True:
            self.update_time()

            if turn_on_from < self.current_second < turn_on_to:
                self.device.on()
                log.send({"hour": self.current_hour, "minute": self.current_minute, "status": "ON"})
            else:
                self.device.off()
                log.send({"hour": self.current_hour, "minute": self.current_minute, "status": "OFF"})

            await uasyncio.sleep(2)#*30)

            