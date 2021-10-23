import uasyncio
from machine import Pin
from time import localtime
from pump import Pump
from leds import Leds

pump_pin = 18
leds_pin = 19

pump_program = Pump(Pin(pump_pin, Pin.OUT))
leds_program = Leds(Pin(leds_pin, Pin.OUT))

event_loop = uasyncio.get_event_loop()

event_loop.create_task((pump_program.start(3, 1)))
event_loop.create_task((leds_program.start(0, 20)))

event_loop.run_forever()


# async def main():
#     uasyncio.create_task((pump_program.start(3, 1)))
#     uasyncio.create_task((leds_program.test()))
#     while True:
#         print("test")
#         await uasyncio.sleep_ms(1000)

# uasyncio.run(main())

# ntptime.settime()

# _, _, _, utc_time_hour, _, _, _, _ = localtime()
# dk_time_hour = utc_time_hour + 2

# _, _, _, _, utc_time_minutes, _, _, _ = localtime()
# dk_time_minutes = utc_time_minutes

# pump_power = Pin(19, Pin.OUT)
# led_lights = Pin(18, Pin.OUT)

# is_pumping = False
# lights_are_on = False

