import neodisplay

class LDR:

    name = "LDR"

    pause_before_reading = 100 # milliseconds

    def __init__(self, pin): # pin to which is attached the ldr
        self.pin = pin

    def start(self):
        pass # There's nothing to start in a LDR ;)
    
    def stop(self):
        pass # There's nothing to stop in a LDR ;)
        
    def takeReading(self):
        return self.pin.read_analog()

    def show_busy(self):
        neodisplay.show_busy(1)