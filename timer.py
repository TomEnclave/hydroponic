import time

class Automation:
    
    from machine import Pin
    import ntptime
    
    ntptime.settime()
    
    def __init__(self, device = Pin(2, Pin.OUT), timezone_relative_to_utc = 2):
        self.device = device
        self.timezone_relative_to_utc = timezone_relative_to_utc
    
    def update_time(self):
        self.current_year, self.current_month, self.current_day, self.utc_time_hour, self.current_minute, self.current_second, _, _ = time.localtime()
        self.current_hour = self.utc_time_hour + self.timezone_relative_to_utc
        #self.epoch_time_in_seconds = time.mktime(time.localtime())
    
    """ #match doesn't work in micropython?
    def current(unit):
        match unit:
            case 'year':
                return time.localtime()[0]
            case 'month':
                return time.localtime()[1]
            case 'day':
                return time.localtime()[2]
            case 'hour':
                return time.localtime()[3]
            case 'minute':
                return time.localtime()[4]
            case 'second':
                return time.localtime()[5]
            case 'weekday':
                return time.localtime()[6]
            case 'yearday':
                return time.localtime()[7] """

    
    
    
