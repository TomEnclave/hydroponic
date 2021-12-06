# hydroponic
Automation for hydroponic vertical garden/farm

#
###  config.py file should be created with parameters:
```
WIFI_NAME = "your-wifi-name"
WIFI_PASSWORD = "your-wifi-password"
CLOUD_SERVER = "https://your-fire-base-server.firebasedatabase.app/" #Don't forget slash in the end
```

### PH Meter 1.1 + Chinese Probe (not the original, which comes with DF Robot PH Kit)
1. Calibrate Potentiometer:
    - Clockwise - decreases range
    - Counter Clockwise - increases range
    - You want your use-case range  to cover the ADC attenuation range
    - Put the most acidic liquid in one glass (For example Cola is PH 2.6-2.7)
    - And most alkaline in another glass (neutral PH 7 distilled (or tap) water is good enough if you are using PH meter only for plant solutions)
    - Measure the voltage from analog and ground on PH Meter:
        - The voltage for Cola should be close to 0v
        - The voltage for Distilled water should be between 1.5-2v
        - Set ADC attenuation to 2v, so it would cover most of the range
        - If your are expecting more acidic or alkaline results, than increase the range, but also increase esp32 adc attenuation from 2v to 3.6v
2. Calibrate PH function
    - Use 2 calibration solutions, PH 4.0 and PH 7.0
    - Set ph_calibration to True in config.py
    - Calibration program should automatically detect if the probe is in PH 4 or PH 7 by approximating the usual voltage ranges, and imidiatly link certain voltage to  PH 4 or PH 7
    - After completing calibration in one solution, put it in another (after drying the probe)