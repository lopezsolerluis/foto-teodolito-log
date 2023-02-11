class LDR:

    pause_before_reading = 100 # milliseconds

    def __init__(self, pin): # pin to which is attached the ldr
        self.pin = pin

    def takeReading(self):
        return self.pin.read_analog()

    def start(self):
        pass # There's nothing to start in a LDR ;)
    
    def stop(self):
        pass # There's nothing to stop in a LDR ;)