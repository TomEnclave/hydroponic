import uasyncio
import machine
import framebuf
import db
import logo_bitmap
from debug import log
debug = True

class Display():
    
    def __init__(self, id="other", screen_width = 128, screen_height = 64, scl_pin = 22, sda_pin = 21, sh1106_address = 0x3c):
        super().__init__()
        self.id = id
        self.i2c = machine.I2C(scl = machine.Pin(scl_pin),sda = machine.Pin(sda_pin))
        self.refreshing = False
        self.sh1106_address = sh1106_address
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_rows = screen_height // 8
        self.screen_size = self.screen_rows * self.screen_width
        self.screen_buffer = bytearray(self.screen_size)

        self.display = framebuf.FrameBuffer1(self.screen_buffer, self.screen_width, self.screen_height)
        
        self.power_on_register = 0xae
        self.rows_register = 0xb0
        self.column_low_register = 0x00
        self.column_high_register = 0x10
        self.set_command = 0x80
        self.data_command = 0x40

        self.i2c.writeto(self.sh1106_address, bytearray([self.set_command, self.power_on_register | True]))

        self.display.fill(0)
        #self.screen_buffer = gear #self.screen_buffer | gear
        self.display.vline(64, 0, 32, 0xffff)
        self.display.hline(0, 32, 128, 0xffff)
        self.display.vline(95, 32, 32, 0xffff)
        """ print("MEMORY SCREEN")
        print(self.screen_buffer)
        f = open("screen_buffer.txt", 'wb')
        print("FILE SCREEN")
        f.write(self.screen_buffer)
        f.close()
        f = open("screen_buffer.txt", 'rb')
        print(f.read())
        f.close() """
        self.local_db = db.Database(self.id)
    
    def bytearray_bitwise_and(self, bytearray1, bytearray2):
        return bytearray([a & b for a, b in zip(bytearray1, bytearray2)])
    
    def bytearray_bitwise_difference(self, bytearray1, bytearray2):
        return bytearray([a & ~b for a, b in zip(bytearray1, bytearray2)])
    
    def bytearray_bitwise_xor(self, bytearray1, bytearray2):
        return bytearray([a ^ b for a, b in zip(bytearray1, bytearray2)])
    
    def bytearray_bitwise_or(self, bytearray1, bytearray2):
        return bytearray([a | b for a, b in zip(bytearray1, bytearray2)])
    
    def refresh(self):

        while self.refreshing:
            uasyncio.sleep_ms(10)
        self.refreshing = True

        data_full = self.local_db.load_data_all()
        
        log("-----------------Screen-----------------", debug)
        log("DEVICE ID: {0} | DEVICE DATA: {1} | DATA LENGTH: {2}".format(self.id, data_full[self.id][-1] if len(data_full[self.id]) > 0 else "no data", len(data_full[self.id])), debug)

        left_side = 0
        right_side = int(self.screen_width/2 + 2)
        line_number = [0, 8, 16, 24, 33, 41, 49, 57]
        try:
            data = data_full["ph"][-1]
            self.display.fill_rect(left_side, line_number[0], 64 - 1, 8, 0x0000)
            self.display.text("PH:{0}".format(round(data["ph"], 3)), left_side, line_number[0], 1)
        except:
            pass
        try:
            data = data_full["ec"][-1]
            self.display.fill_rect(right_side, line_number[0], 64, 8, 0x0000)
            self.display.text("EC:{0}".format(round(data["ec"], 3)), right_side, line_number[0], 1)
        except:
            pass
        try:
            data = data_full["ec"][-1]
            self.display.fill_rect(left_side, line_number[1], 64 - 1, 8, 0x0000)
            self.display.text("TDS:{0}".format(round(data["ppm"])), left_side, line_number[1], 1)
        except:
            pass
        try:
            data = data_full["ec"][-1]
            self.display.fill_rect(right_side, line_number[1], 64, 8, 0x0000)
            self.display.text("TEMP:{0}".format(round(data["temperature"])), right_side, line_number[1], 1)
        except:
            pass
        try:
            data = data_full["air"][-1]
            self.display.fill_rect(left_side, line_number[2], 64 - 1, 8, 0x0000)
            self.display.text("AIR:{0}".format(data["air temperature"]), left_side, line_number[2], 1)
        except:
            pass
        try:
            data = data_full["air"][-1]
            self.display.fill_rect(right_side, line_number[2], 64, 8, 0x0000)
            self.display.text("HUMD:{0}".format(data["air humidity"]), right_side, line_number[2], 1)
        except:
            pass
        try:
            data = data_full["light"][-1]
            self.display.fill_rect(left_side, line_number[3], 64 - 1, 8, 0x0000)
            self.display.text("CCT:{0}".format(round(data["cct"])), left_side, line_number[3], 1)
        except:
            pass
        try:
            data = data_full["light"][-1]
            self.display.fill_rect(right_side, line_number[3], 64, 8, 0x0000)
            self.display.text("PPFD:{0}".format(round(data["ppfd"], 1)), right_side, line_number[3], 1)
        except:
            pass
        try:
            data = data_full["light"][-1]
            self.display.fill_rect(left_side, line_number[4], 94, 8, 0x0000)
            self.display.text("r{0}g{1}b{2}".format(round(data["rgb"][0]),round(data["rgb"][1]),round(data["rgb"][2])), left_side, line_number[4], 1)
        except:
            pass
        try:
            data = data_full["water_pipe"][-1]
            self.display.fill_rect(left_side, line_number[5], 94, 8, 0x0000)
            self.display.text("W.level {0}".format(round(data["water level"])), left_side, line_number[5], 1)
        except:
            pass
        try:
            data = data_full["power"][-1]
            self.display.fill_rect(left_side, line_number[6], 94, 8, 0x0000)
            self.display.text("Power {0} w".format(round(data["consumption"])), left_side, line_number[6], 1)
        except:
            pass
        try:
            data = data_full["pump"][-1]
            self.display.fill_rect(left_side, line_number[7], 94, 8, 0x0000)
            self.display.text("Pump {0} {1}".format(data["status"], data["minute"]), left_side, line_number[7], 1)
        except:
            pass
        if self.id is "other": 
            self.display.fill(0)
            self.display.text("{0}{1}".format(self.id, data), right_side, 8, 1)
        #log("SCREEN BUFFER: {0}".format(self.screen_buffer), debug)
        log("----------------------------------------", debug)

        """ #self.clean_buffer = self.bytearray_bitwise_and(self.screen_buffer, byte_array_from_buffer)
        difference_in_first_buffer = self.bytearray_bitwise_difference(self.screen_buffer, byte_array_from_buffer)
        difference_in_second_buffer = self.bytearray_bitwise_difference(byte_array_from_buffer, self.screen_buffer)
        combined_buffer = self.bytearray_bitwise_or(difference_in_first_buffer, difference_in_second_buffer)
        """
        geared_buffer = self.bytearray_bitwise_or(self.screen_buffer, logo_bitmap.turn_the_gear()) #gear_vlsb)

        for row in range(self.screen_rows):
            self.i2c.writeto(self.sh1106_address, bytes([self.set_command, self.rows_register | row]))
            self.i2c.writeto(self.sh1106_address, bytes([self.set_command, self.column_low_register | 0b00000010]))
            self.i2c.writeto(self.sh1106_address, bytes([self.set_command, self.column_high_register | 0b00000000]))
            self.i2c.writeto(self.sh1106_address, bytes([self.data_command]) + geared_buffer[(self.screen_width * row) : (self.screen_width * row + self.screen_width)])
        
        self.refreshing = False