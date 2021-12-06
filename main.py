import uasyncio
import config_main
from machine import Pin, ADC
from time import localtime
from pump import Pump
from leds import Leds
from temperature import Temp
from ec_sensor import Ec
from ph_sensor import Ph

pump_program = Pump(Pin(config_main.pump_pin, Pin.OUT))
leds_program = Leds(Pin(config_main.leds_pin, Pin.OUT))

#temperature_sensor = Temp(ADC(Pin(config_main.temperature_pin)))
ec_sensor= Ec()
ph_sensor = Ph(calibrating = config_main.ph_calibration)

async_loop = uasyncio.get_event_loop()
async_loop.create_task((
                        pump_program.start(
                            config_main.pump_minutes_to_work, 
                            config_main.pump_minutes_to_rest)))
async_loop.create_task((
                        leds_program.start(
                            config_main.leds_turn_on_from, 
                            config_main.leds_turn_off_from)))
async_loop.create_task((
                        ec_sensor.start_log(
                            config_main.ppm_update_interval_sec)))
async_loop.create_task((
                        ph_sensor.start_log(
                            config_main.ph_update_interval_sec)))
# async_loop.create_task((
#                         temperature_sensor.start_log(
#                             config_main.temperature_update_interval_sec)))
async_loop.run_forever()