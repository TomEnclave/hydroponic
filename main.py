import uasyncio
from machine import Pin, ADC
from time import localtime
from pump import Pump
from leds import Leds
from temperature import Temp

pump_pin = 18
leds_pin = 19
temperature_pin = 32

pump_minutes_to_work = 3
pump_minutes_to_rest = 1

leds_turn_on_from = 0
leds_turn_off_from = 20

temperature_update_interval_sec = 3

pump_program = Pump(Pin(pump_pin, Pin.OUT))
leds_program = Leds(Pin(leds_pin, Pin.OUT))
temperature = Temp(ADC(Pin(temperature_pin)))
temperature.calibrate()

event_loop = uasyncio.get_event_loop()

event_loop.create_task((pump_program.start(pump_minutes_to_work, pump_minutes_to_rest)))
event_loop.create_task((leds_program.start(leds_turn_on_from, leds_turn_off_from)))
event_loop.create_task((temperature.start_log(temperature_update_interval_sec)))

event_loop.run_forever()

