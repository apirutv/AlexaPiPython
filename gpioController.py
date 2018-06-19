#!/usr/bin/python
import RPi.GPIO as GPIO
import time

class GPIOController():
    bcmPinNumber = -1
    gpioMode = GPIO.LOW

    def __init__(self, bcmPinNumber, gpioMode):
        self.bcmPinNumber = bcmPinNumber
        self.gpioMode = gpioMode
        self.setupPin()
 
    def setupPin(self):
    	GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bcmPinNumber, self.gpioMode)
 
    def cleanupGPIO(self):
    	GPIO.cleanup();
    
    def output(self,value):
    	GPIO.output(self.bcmPinNumber,value) 
    	print("*** SET BCM PIN " + str(self.bcmPinNumber) + " to " + str(value))
    	
    def input(self):
    	return GPIO.input(self.bcmPinNumber)

"""    	
# TEST SCRIPT    	    	
con = GPIOController(14,GPIO.LOW)

try:
    con.output(GPIO.HIGH)
    print(con.input())
    time.sleep(2)
    con.output(GPIO.LOW)
    print(con.input())
    con.cleanupGPIO()

# End program cleanly with keyboard
except KeyboardInterrupt:
    print " Quit"

    # Reset GPIO settings

    GPIO.cleanup()
"""     	
