import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
	button = GPIO.input(17)
	print button

	
