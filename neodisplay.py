from microbit import pin16
import neopixel
import colors

np = neopixel.NeoPixel(pin16, 4)

def show_state(index, color):
    np.clear()
    np[index] = color
    np.show()

def show_busy(index):
    show_state(index,colors.busy)

def show_available(index):
    show_state(index,colors.available)

def show_clear():
    np.clear()