# Adapted from https://github.com/octaprog7/BH1750

from microbit import i2c
import time

_BH1750_ADDRESS = 0x23

class BH1750:

    pause_before_reading = 200 # milliseconds

    def send_cmd(self, cmd):
        i2c.write(_BH1750_ADDRESS, bytes([cmd]))

    def configure(self, continuous=True, highResolution=True):
        cmd = 0b0001_0000 if continuous else 0b0010_0000
        cmd |= 0 if highResolution else 0b11
        self.send_cmd(cmd)
        time.sleep_ms(200)
        self.continuous = continuous
        self.highResolution = highResolution 

    def set_power(self, on):
        if on:
            self.send_cmd(1)
            self.configure(self.continuous, self.highResolution)
        else:
            self.send_cmd(0)

    def start(self):
        self.set_power(True)

    def stop(self):
        self.set_power(False)

    def __init__(self, continuous=True, highResolution=True):
        self.continuous = continuous
        self.highResolution = highResolution 
        self.start()             
        
    def readLightLevel(self):
        buf = i2c.read(_BH1750_ADDRESS, 2)
        level = buf[0] << 8 | buf[1]
        return level / 1.2 # See datasheet

    def takeReading(self):
        return self.readLightLevel()