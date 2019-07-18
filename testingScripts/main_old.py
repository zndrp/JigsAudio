#/usr/bin/env python
# Zander is a bad man who doesn't comment his scripts properly
import os
import pyaudio
import wave
import sys
import RPi.GPIO as GPIO
import time

#Globals here:
AUDIODIR = "/home/pi/audiorecordings"
light = False

def init():
	#setup GPIO Pins
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	#this is the white LED
	GPIO.setup(18,GPIO.OUT)

	#this is the white button
	GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)

def captureAudio(puz_id):
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 48000
	CHUNK = 1024
	RECORD_SECONDS = 30
	WAVE_OUTPUT_FILENAME = puz_id
	 
	audio = pyaudio.PyAudio()
	 
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
	                	rate=RATE, input=True,
	                	frames_per_buffer=CHUNK)
	print "recording..."
	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		try:	        
			data = stream.read(CHUNK)

		except IOError as ex:
			print "################# IOError Caught!!! ###################" 
			if ex[1] != pyaudio.paInputOverflowed:
				raise
			data = '/x00' * CHUNK
    
		frames.append(data)
	    #flashes the light
		global light
		if i % 24  == 0:
			if light:
				light_off()
			else:
			    light_on()
	
	print "finished recording"
 
	# stop Recording
	stream.stop_stream()
	stream.close()
	audio.terminate()
	 
	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()

def light_on():
	global light
	GPIO.output(18,GPIO.HIGH)
	light = True

def light_off():
	global light
	light = False
	GPIO.output(18,GPIO.LOW)

def light_flash(flashfrq, flashno):
	flashes = 0
	while flashes < flashno:
		GPIO.output(18,GPIO.HIGH)
		time.sleep(flashfrq)
		GPIO.output(18,GPIO.LOW)
		time.sleep(flashfrq)
		flashes = flashes + 1

def main():
	
	while True:
		#grab the puzzle piece ID, and format it into an mp3 file
		current_time = time.time()
		print current_time
		puz_id = raw_input("What's the number of the puzzle piece? (scan the piece): ")
		time_scanned = time.time()
		print time_scanned
	
		diff_time = time_scanned - current_time
		print diff_time

		if diff_time > 1:
			break

	print puz_id
	clipno = 1
	
	#is there already audio? Find a filename to use:
		
	while os.path.exists(puz_id + "-" + str(clipno) + ".wav"):
		clipno = clipno + 1
	puz_id = puz_id + "-" + str(clipno) + ".wav"

	# so now we have the valid clip number and file, we can record into it:
	scan_time = time.time()

	print "ready to record"

	while True:
		button = GPIO.input(17)
		light_on()
		if button == False:
			button = GPIO.input(17)
			#print "button pressed, light off, recording starting..."
			captureAudio(puz_id)
			print "sound recordeded to: " + puz_id
			flashfrq = 0.1
			flashno = 6
			light_flash(flashfrq, flashno)
			break

		current_time = time.time()
		time_since_scan = current_time - scan_time

		if time_since_scan > 10:
			print "Button Not Pressed - Timed Out"
			light_off()
			break
	

	return True	

if __name__ == "__main__":
	os.chdir(AUDIODIR)	
	init()
	light_flash (0.5, 4)
	light_off()
	while main():
		time.sleep(1)
