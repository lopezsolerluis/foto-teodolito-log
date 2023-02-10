from microbit import *
import log
from pca9685 import *
from bh1750 import *
from math import cos, radians

pca = PCA9685()
log.set_labels('altitude', 'azimuth', 'measure', timestamp=log.SECONDS)

measureInstrument = "BH1750" # "LDR" or "BH1750"
servo = 1 # Servo channel
stepper = 1 # Stepper channel
reduction = 2 # Relation between the gears of the 'foto-teodolito'
LDRpin = pin1 # pin to which the LDR is attached
pause_before_measure = 200 # milliseconds
min_altitude = 30 # We don't want to measure the buildings, right? :D
delta_altitude = 30

bh1750 = BH1750() if measureInstrument == "BH1750" else None

def takeReadingLDR():
    return LDRpin.read_analog()    

def takeReadingBH1750():
    if bh1750:
        return bh1750.readLightLevel()
    else:
        return 0 # Don't like this...

def takeReading():
    if measureInstrument == "BH1750":
        return takeReadingBH1750()
    else:
        return takeReadingLDR()
    
# Wait until Button 'A' is pressed. This way, we can sinchronize the measures with an external clock or watch
while not button_a.was_pressed():
    pass

for altitude in range(min_altitude, 90+delta_altitude, delta_altitude):
    pca.setServoDegrees(servo, altitude)
    steps_in_almucantarat = round(360*cos(radians(altitude)) / delta_altitude) if (altitude != 90) else 1
    delta_azimuth = 360 / steps_in_almucantarat
    azimuth = 0
    while azimuth < 360:
        sleep(pause_before_measure)
        measure = takeReading()
        log.add({
            'altitude': altitude,
            'azimuth': azimuth,
            'measure': measure
            })
        if steps_in_almucantarat != 1:
            pca.moveStepperDegreesBlocking(stepper, delta_azimuth*reduction)
        azimuth += delta_azimuth

pca.setServoDegrees(servo, 0) # Parking position