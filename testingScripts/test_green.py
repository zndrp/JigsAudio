import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23,GPIO.OUT)

def green_on():
    GPIO.output(23,GPIO.HIGH)
    
def green_off():
    GPIO.output(23,GPIO.LOW)


while True:
    green_on()
    time.sleep(.1)
    green_off()
    time.sleep(.1)
