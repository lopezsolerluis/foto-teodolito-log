from microbit import *
import log
from pca9685 import *
from bh1750 import *
from ldr import *
from math import cos, radians

pca = PCA9685()

sensor = BH1750() # sensor = BH1750() or LDR(pin1)

servo = 1 # Servo channel
stepper = 1 # Stepper channel
reduction = 2 # Relation between the gears of the 'foto-teodolito'
min_altitude = 30 # We don't want to measure the buildings, right? :D
delta_altitude = 30
    
def take_readings(begin_log=True):
    sensor.start()
    if begin_log:
        log.set_labels('altitude', 'azimuth', 'measure', timestamp=log.SECONDS)
    for altitude in range(min_altitude, 90+delta_altitude, delta_altitude):
        pca.setServoDegrees(servo, altitude)
        steps_in_almucantarat = round(360*cos(radians(altitude)) / delta_altitude) if (altitude != 90) else 1
        delta_azimuth = 360 / steps_in_almucantarat
        azimuth = 0
        while azimuth < 360:
            sleep(sensor.pause_before_reading)
            measure = sensor.takeReading()
            log.add({
                'altitude': altitude,
                'azimuth': azimuth,
                'measure': measure
                })
            if steps_in_almucantarat != 1:
                pca.moveStepperDegreesBlocking(stepper, delta_azimuth*reduction)
            azimuth += delta_azimuth
    pca.setServoDegrees(servo, 0) # Parking position
    sensor.stop()

# Wait until Button 'A' is pressed. This way, we can sinchronize the measures with an external clock or watch
while not button_a.was_pressed():
    pass

take_readings()
sleep(1000)
take_readings(False)