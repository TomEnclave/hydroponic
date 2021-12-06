pin_thermistor = 36
pin_ec_read = 35
pin_ec_ground = 19
pin_ec_power = 26

calibration_ec = 1.38 # Used only for calibration, EC value of Calibration solution in siemens/cm

resistor = 1000 # R1
pin_resistance = 25 # Ra - Pin resistance of ESP32 (compared to 25 in arduino), according to page 43 of esp32_datasheet_en.pdf
pin_voltage = 3.3 # Esp32 pin voltage is 3.3v / 5v on Arduino UNO

#The value below will change depending on what chemical solution we are measuring
#0.019 is generaly considered the standard for plant nutrients [google "Temperature compensation EC" for more info
temperature_coeficient = 0.019 #this changes depending on what chemical we are measuring

ppm_conversion = 0.64 # USA = 0.5 / EU = 0.64 / Australia = 0.7

K = 0.96 #  K - Cell Constant. Value which needs to be calibrated to show precise EC value. Normally :- 2.88 for US plugs / 1.76 for EU plugs