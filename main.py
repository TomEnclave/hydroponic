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

