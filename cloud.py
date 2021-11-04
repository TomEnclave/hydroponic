import config
import ujson
import uasyncio
import urequests

class Iot:

    def __init__(self, data_name, cloud = config.CLOUD_SERVER):
        self.server = cloud
        self.data_name = data_name
        self.put_connection_status = "closed"
    
    def send(self, data):
        while self.put_connection_status == "openned":
            uasyncio.sleep_ms(100)
        self.put_connection_status = "openned"
        parsed_data = ujson.dumps(data)
        put_connection = urequests.post(self.server + self.data_name + ".json", data=parsed_data)
        put_connection.close()
        self.put_connection_status = "closed"