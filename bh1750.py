# Adapted from https://github.com/octaprog7/BH1750

from microbit import i2c
import time

_BH1750_ADDRESS = 0x23

class BH1750:

    pause_before_reading = 200 # milliseconds

    def __init__(self):
        i2c.write(_BH1750_ADDRESS, bytes([0b0001_0000])) # Continuous mode
        time.sleep_ms(200)
        # TODO: set different modes    
        
    def readLightLevel(self):
        buf = i2c.read(_BH1750_ADDRESS, 2)
        level = buf[0] << 8 | buf[1]
        return level / 1.2

    def takeReading(self):
        return self.readLightLevel()