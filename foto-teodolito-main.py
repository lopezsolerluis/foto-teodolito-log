# Imports go at the top
from microbit import *
import log
from pca9685 import *

pca = PCA9685()
log.set_labels('altitude', 'azimuth', 'measure', timestamp=log.SECONDS)

servo = 1 # Servo channel
stepper = 1 # Stepper channel
reduction = 2 # Relation between the grears of the 'foto-teodolito'
pause_between_measures = 200 # milliseconds
min_altitude = 30
delta_alpha = 30
measure = 0

# Wait until Button 'A' is pressed. This way, we can sinchronize the measures with an external clock or watch
while not button_a.was_pressed():
    pass

for altitude in range(min_altitude, 90+delta_alpha, delta_alpha):
    pca.setServoDegrees(servo, altitude)
    delta_azimuth = delta_alpha # TODO: change in function of altitude
    azimuth = 0
    while azimuth < 360:
        sleep(pause_between_measures)
        # TODO: take reading
        log.add({
            'altitude': altitude,
            'azimuth': azimuth,
            'measure': measure
        })
        pca.moveStepperDegreesBlocking(stepper, delta_azimuth*reduction)
        azimuth += delta_azimuth
    
    
    


    
            