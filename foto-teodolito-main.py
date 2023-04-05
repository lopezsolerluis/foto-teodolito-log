from microbit import *
import log
from pca9685 import *
from bh1750 import *
from ldr import *
from math import cos, radians
import neodisplay
import colors
import radio
import time

servo = 1 # Servo channel
stepper = 1 # Stepper channel
ldr_pin = pin1 # pin to which is attached the ldr
reduction = 2 # Relation between the gears of the 'foto-teodolito'
min_altitude = 20 # We don't want to measure the buildings, right? :D
delta_altitude = 5

pca = PCA9685()
radio.off()

first_reading = True

def show_available():
    neodisplay.show_available(0)

def show_remote_control_available():
    neodisplay.show_state(3,colors.remote_available)


def reset_log():
    global first_reading
    log.delete()
    log.set_labels('sensor name','altitude', 'azimuth', 'measure', timestamp=log.SECONDS)
    first_reading = False


def take_one_reading(sensor, altitude, azimuth):
    sleep(sensor.pause_before_reading)
    log.add({
             'sensor name': sensor.name,
             'altitude': altitude,
             'azimuth': azimuth,
             'measure': sensor.takeReading()
              })


def take_remote_reading(sensor, altitude, azimuth):
    if first_reading:
        reset_log()
    sensor.start()
    sensor.show_busy()
    take_one_reading(sensor, altitude, azimuth)
    sensor.stop()
    show_remote_control_available()


def take_readings(sensor):
    if first_reading:
        reset_log()
    sensor.start()
    sensor.show_busy()
    for altitude in range(min_altitude, 90+delta_altitude, delta_altitude):
        pca.setServoDegrees(servo, altitude)
        steps_in_almucantarat = round(360*cos(radians(altitude)) / delta_altitude) if (altitude != 90) else 1
        delta_azimuth = 360 / steps_in_almucantarat
        for step in range(steps_in_almucantarat):
            azimuth = step * delta_azimuth
            take_one_reading(sensor, altitude, azimuth)
            if steps_in_almucantarat != 1:
                pca.moveStepperDegreesBlocking(stepper, delta_azimuth*reduction)
    pca.setServoDegrees(servo, 0) # Parking position
    sensor.stop()
    show_available()


def remote_control_mode():
    show_remote_control_available()
    sleep(500) # For not exiting upon arriving... :p
    radio.on()

    altitude_resolution = 3
    azimuth_resolution = 10
    azimuth = 0
    previous_vel_azimuth = 0
    current_vel_azimuth = 0
    start_time = 0

    def getAzimuth():
        degrees_moved = time.ticks_diff(time.ticks_ms(), start_time) * 36 / 1024 / reduction * previous_vel_azimuth # + or -?
        return (azimuth + degrees_moved) % 360

    pca.setServoDegrees(servo, 0) # For avoiding random reading of servo position at the beginning

    while not pin_logo.is_touched():
        msg = radio.receive()
        if msg is not None:
            button = msg[0:1]
            altitude_desired = int(msg[1:4])
            vel_azimuth = int(msg[4:7])

            altitude = pca.getServoDegrees(servo)

            if abs(altitude_desired - altitude) > altitude_resolution:
                if altitude_desired > altitude:
                    altitude += altitude_resolution
                else:
                    altitude -= altitude_resolution

            pca.setServoDegrees(servo, altitude)

            if vel_azimuth > azimuth_resolution:
                current_vel_azimuth = 1
            elif vel_azimuth < -azimuth_resolution:
                current_vel_azimuth = -1
            else:
                current_vel_azimuth = 0

            if current_vel_azimuth != 0 and current_vel_azimuth != previous_vel_azimuth: # Has started or changed direction
                if previous_vel_azimuth != 0: # Has changed direction
                    azimuth = getAzimuth()
                direction = False if current_vel_azimuth == 1 else True
                pca.startStepper(stepper, direction)
                start_time = time.ticks_ms()
            elif current_vel_azimuth == 0 and previous_vel_azimuth != 0: # Has stopped!
                pca.stopStepper(stepper)
                azimuth = getAzimuth()

            previous_vel_azimuth = current_vel_azimuth

            if button == 'A' or button == 'B':
                azimuth = getAzimuth()
                start_time = time.ticks_ms()
                take_remote_reading(LDR(ldr_pin) if button=='A' else BH1750(), altitude, azimuth)

        sleep(50)
    radio.off()
    show_available()
    pca.setServoDegrees(servo, 0) # Parking position
    sleep(500) # Same as before


show_available()

while True:
    if button_a.is_pressed():
        take_readings(LDR(ldr_pin))
    elif button_b.is_pressed():
        take_readings(BH1750())
    elif pin_logo.is_touched():
        remote_control_mode()
