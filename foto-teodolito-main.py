from microbit import *
import log
from pca9685 import *
from math import cos, radians

pca = PCA9685()
log.set_labels('altitude', 'azimuth', 'measure', timestamp=log.SECONDS)

servo = 1 # Servo channel
stepper = 1 # Stepper channel
reduction = 2 # Relation between the gears of the 'foto-teodolito'
pause_between_measures = 1000 # milliseconds
min_altitude = 30 # We don't want to measure the buildings, rigth? :D
delta_altitude = 30

def takeReading():
    measure = 0 # TODO
    return measure
    
# Wait until Button 'A' is pressed. This way, we can sinchronize the measures with an external clock or watch
while not button_a.was_pressed():
    pass

for altitude in range(min_altitude, 90+delta_altitude, delta_altitude):
    pca.setServoDegrees(servo, altitude)
    steps_in_almucantarat = round(360*cos(radians(altitude)) / delta_altitude) if (altitude != 90) else 1
    delta_azimuth = 360 / steps_in_almucantarat
    azimuth = 0
    while azimuth < 360:
        sleep(pause_between_measures)
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