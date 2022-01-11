import uasyncio
import config_main
from machine import Pin
from pump import Pump
from leds import Leds
from ec_sensor import Ec
from ph_sensor import Ph
from light_sensor import Ppfd
from water_pipe import WaterPipe
from dht11 import Dht11
from consumption import Consumption
from water_tank import WaterTank

pump_program = Pump(Pin(config_main.pump_pin, Pin.OUT))
leds_program = Leds(Pin(config_main.leds_pin, Pin.OUT))

ec_sensor= Ec()
ph_sensor = Ph(calibrating = config_main.ph_calibration)
ppfd_sensor = Ppfd()
water_sensor = WaterPipe()
room_sensor = Dht11()
consumption_sensor = Consumption()
water_tank = WaterTank()

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
async_loop.create_task((
                        ppfd_sensor.start_log(
                            config_main.ppfd_update_interval_sec)))
async_loop.create_task((
                        water_sensor.start_log(
                            1)))
async_loop.create_task((
                        room_sensor.start_log(
                            1)))
async_loop.create_task((
                        consumption_sensor.start_log(
                            1)))
async_loop.create_task((
                        water_tank.start_log(
                            1)))
async_loop.run_forever()