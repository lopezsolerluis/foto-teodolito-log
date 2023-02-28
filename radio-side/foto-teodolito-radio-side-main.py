# Imports go at the top
from microbit import *
import radio

def g_to_degrees(g,minimun=-90,maximum=90):
    "Turns the 'g' value given by the accelerometer to an angle in degrees, restricted between 'minimum' and 'maximum'."
    degree = round(g*90/1000)
    return min(max(degree,minimun),maximum)

def discretize_value(value, step=5):
    "Rounds the given value to the nearest 'step'; e.g., if step=5: 43->45, 2->0, etc."
    return round(value/step) * step
    
while True:
    altitude = g_to_degrees(accelerometer.get_y(),0,90)
    vel_azimuth = g_to_degrees(accelerometer.get_x())
    discrete_altitude = discretize_value(altitude)
    discrete_vel_azimuth = discretize_value(vel_azimuth)

    button = ' '
    if button_a.was_pressed():
        button = 'A'
    elif button_b.was_pressed():
        button = 'B'
        
    msg = "{}{:+03}{:+03}".format(button, discrete_altitude, discrete_vel_azimuth)
    
    radio.send(msg)
    sleep(100)