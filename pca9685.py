# Adapted from https://github.com/KittenBot/pxt-robotbit/blob/master/main.ts

from microbit import i2c
import time
import microbit

_PCA9685_ADDRESS = 0x40
_MODE1 = 0x00
_PRESCALE = 0xFE
_LED0_ON_L = 0x06

_STP_CHA_L = 2047
_STP_CHA_H = 4095
_STP_CHB_L = 1
_STP_CHB_H = 2047
_STP_CHC_L = 1023
_STP_CHC_H = 3071
_STP_CHD_L = 3071
_STP_CHD_H = 1023

v_us_f = 10.8 # (It's supposed to be '10' instead of 10.8...-?-)


class PCA9685:

    def __init__(self):
        self.write(_PCA9685_ADDRESS, _MODE1, 0x00)
        self.setFreq(50)
        for i in range(0, 16):
            self.setPwm(i, 0, 0)

    def write(self, addr, reg, val):
        i2c.write(addr, bytes([reg, val]))

    def read(self, addr, reg):
        i2c.write(addr, bytes([reg]))
        return i2c.read(addr,1)[0]

    def setFreq(self, freq):
        prescale = round(25000000.0 / 4096.0 / freq - 1) # since python 3, round returns int.
        oldmode = self.read(_PCA9685_ADDRESS, _MODE1)
        newmode = (oldmode & 0x7F) | 0x10 # sleep
        self.write(_PCA9685_ADDRESS, _MODE1, newmode) # go to sleep
        self.write(_PCA9685_ADDRESS, _PRESCALE, prescale) # set the prescaler
        self.write(_PCA9685_ADDRESS, _MODE1, oldmode)
        time.sleep_us(5000)
        self.write(_PCA9685_ADDRESS, _MODE1, oldmode | 0xa1)

    def setPwm(self, channel, on, off):
        i2c.write(_PCA9685_ADDRESS, bytes([_LED0_ON_L + 4 * channel,
                                           on & 0xff,
                                           (on >> 8) & 0xff,
                                           off & 0xff,
                                           (off >> 8) & 0xff]))
    
    def setServoDegrees(self, servo, degree): # servo: 1, etc.
        global v_us_f
        v_us = degree * v_us_f + 600 # 0.6 ~ 2.4 
        value = v_us * 4096.0 / 20000
        self.setPwm(servo + 7, 0, round(value))

    def getServoDegrees(self, servo): # servo: 1, etc.
        global v_us_f        
        channel = servo + 7
        addr = _PCA9685_ADDRESS
        i2c.write(addr, bytes([_LED0_ON_L + 4 * channel + 2]))
        buf = i2c.read(addr,2)
        value = buf[1] << 8 | buf[0]
        v_us = value * 20000.0 / 4096.0
        return (v_us - 600) / v_us_f
        
    def releaseServo(self, servo): # servo: 1, etc.
        self.setPwm(servo + 7, 0, 0)

    def setStepper(self, index, dir): # index: 1 or 2, dir: True or False
       if (index == 1):
           if (dir): 
               self.setPwm(0, _STP_CHA_L, _STP_CHA_H)
               self.setPwm(2, _STP_CHB_L, _STP_CHB_H)
               self.setPwm(1, _STP_CHC_L, _STP_CHC_H)
               self.setPwm(3, _STP_CHD_L, _STP_CHD_H)
           else:
               self.setPwm(3, _STP_CHA_L, _STP_CHA_H)
               self.setPwm(1, _STP_CHB_L, _STP_CHB_H)
               self.setPwm(2, _STP_CHC_L, _STP_CHC_H)
               self.setPwm(0, _STP_CHD_L, _STP_CHD_H)
       else:
           if (dir):
               self.setPwm(4, _STP_CHA_L, _STP_CHA_H)
               self.setPwm(6, _STP_CHB_L, _STP_CHB_H)
               self.setPwm(5, _STP_CHC_L, _STP_CHC_H)
               self.setPwm(7, _STP_CHD_L, _STP_CHD_H)
           else:
               self.setPwm(7, _STP_CHA_L, _STP_CHA_H)
               self.setPwm(5, _STP_CHB_L, _STP_CHB_H)
               self.setPwm(6, _STP_CHC_L, _STP_CHC_H)
               self.setPwm(4, _STP_CHD_L, _STP_CHD_H)

    def stopStepper(self, index):
        for i in range(0,4) if (index == 1) else range(4,8):
            self.setPwm(i, 0, 0)
    
    def moveStepperDegrees(self, index, degrees): # index: 1 or 2    
        self.setStepper(index, degrees > 0)
        delta_ms = 10260 * abs(degrees) / 360 # microbit.sleep() accepts floats. It was 10240 (?)
        return delta_ms # returns milliseconds to stop

    def moveStepperDegreesBlocking(self, index, degrees): # index: 1 or 2
        delta_ms = self.moveStepperDegrees(index, degrees)
        microbit.sleep(delta_ms)
        self.stopStepper(index)
        
    def startStepper(self, index, clockwise=True): # index: 1 or 2
        self.setStepper(index, clockwise)

if __name__=='__main__':   

    pca = PCA9685()
    pca.setServoDegrees(1, 0) 
    delta = pca.moveStepperDegrees(1, 90)
    time.sleep_ms(delta)
    pca.stopStepper(1)
    
