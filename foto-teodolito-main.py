from microbit import *
import log
from pca9685 import *
from bh1750 import *
from ldr import *
from math import cos, radians
import neodisplay
import colors
import radio

servo = 1 # Servo channel
stepper = 1 # Stepper channel
ldr_pin = pin1 # pin to which is attached the ldr
reduction = 2 # Relation between the gears of the 'foto-teodolito'
min_altitude = 20 # We don't want to measure the buildings, right? :D
delta_altitude = 10

pca = PCA9685()
radio.off()

first_reading = True

def show_available():
    neodisplay.show_available(0)

def show_remote_control_available():
    neodisplay.show_state(3,colors.remote_available)

    
def take_readings(sensor):
    global first_reading
    if first_reading:
        log.delete()
        log.set_labels('altitude', 'azimuth', 'measure', timestamp=log.SECONDS)
        first_reading = False
    sensor.start()
    sensor.show_busy()
    for altitude in range(min_altitude, 90+delta_altitude, delta_altitude):
        pca.setServoDegrees(servo, altitude)
        steps_in_almucantarat = round(360*cos(radians(altitude)) / delta_altitude) if (altitude != 90) else 1
        delta_azimuth = 360 / steps_in_almucantarat
        azimuth = 0
        while azimuth < 360:
            sleep(sensor.pause_before_reading)
            log.add({
                'altitude': altitude,
                'azimuth': azimuth,
                'measure': sensor.takeReading()
                })
            if steps_in_almucantarat != 1:
                pca.moveStepperDegreesBlocking(stepper, delta_azimuth*reduction)
            azimuth += delta_azimuth
    pca.setServoDegrees(servo, 0) # Parking position
    sensor.stop()
    show_available()


def remote_control_mode():
    show_remote_control_available()
    sleep(500) # For not exiting upon arriving... :p
    radio.on()
    altitude = 0
    vel_azimuth = 0
    while not pin_logo.is_touched():
        msg = radio.receive()
        if msg is not None:
            altitude = int(msg[0:3])
            vel_azimuth = int(msg[3:6])
        
            pca.setServoDegrees(1,altitude)
            if vel_azimuth > 10:
                pca.startStepper(1, False)
            elif vel_azimuth < -10:
                pca.startStepper(1, True)
            else:
                pca.stopStepper(1)
        sleep(50)
    radio.off() 
    show_available()
    sleep(500) # Same as before
  
    
show_available()

while True:
    if button_a.is_pressed():
        take_readings(LDR(ldr_pin))
    elif button_b.is_pressed():
        take_readings(BH1750())
    elif pin_logo.is_touched():
        remote_control_mode()