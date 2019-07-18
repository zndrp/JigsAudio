import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(18,GPIO.OUT) #this is the red LED
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP) #this is the red button
GPIO.setup(23,GPIO.OUT) #this is the green LED
GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
	green = GPIO.input(27)
	red = GPIO.input(17)

	if not red:
		print "red"

	if not green:
		print "green"

#	time.sleep(0.3)
