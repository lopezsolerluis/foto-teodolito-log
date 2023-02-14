from microbit import *
import log
from pca9685 import *
from bh1750 import *
from ldr import *
from math import cos, radians

pca = PCA9685()

servo = 1 # Servo channel
stepper = 1 # Stepper channel
ldr_pin = pin1 # Pin to which LDR is attached
reduction = 2 # Relation between the gears of the 'foto-teodolito'
min_altitude = 30 # We don't want to measure the buildings, right? :D
delta_altitude = 30

first_reading = True

def take_readings(sensor):
    global first_reading
    sensor.start()
    if first_reading:
        log.set_labels('altitude', 'azimuth', 'measure', timestamp=log.SECONDS)
        first_reading = False
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

while True:
    if button_a.is_pressed():
        take_readings(LDR(ldr_pin))
    elif button_b.is_pressed():
        take_readings(BH1750()) 