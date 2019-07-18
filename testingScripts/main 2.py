#/usr/bin/env python
# Zander is a bad man who doesn't comment his scripts properly
import os
import pyaudio
import wave
import sys
import RPi.GPIO as GPIO
import time

#GLOBALS HERE:
#this is where the audio is going to be recorded to:
AUDIODIR = "/home/pi/audiorecordings"
#Set the light status as false
light = False
#Something to do with the format - not too sure what.
FORMAT = pyaudio.paInt16
#Change to 2 for stereo mic.
CHANNELS = 1
#Quality of the audio recording:
RATE = 48000
#No. of chunks. No idea what this is?!
CHUNK = 1024
#the longest recording possible (in seconds)
RECORD_SECONDS = 120

#do this before setting doing anything else.
def init():
	#setup GPIO Pins
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	#this is the white LED
	GPIO.setup(18,GPIO.OUT)

	#this is the white button
	GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP)

def captureAudio(puz_id):
	puz_id = puz_id 
	audio = pyaudio.PyAudio()
	 
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
	                	rate=RATE, input=True,
	                	frames_per_buffer=CHUNK)
	print "Recording..."
	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		try:	        
			data = stream.read(CHUNK)

		except IOError as ex:
			print "IOError Caught!" 
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

		if GPIO.input(17) == False and i > 200:
			break

	
	print "finished recording"
 	stop_rec(stream, audio, puz_id, frames)


def stop_rec (stream, audio, puz_id, frames):
	WAVE_OUTPUT_FILENAME = puz_id
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
	
		#this will look for the last scan. If the scan was made within 1 second of the scipt being ready, they will be discarded.
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

	#take the time the puzzle was scanned to later compare (to look for errors of multiple scans)
	scan_time = time.time()

	print "ready to record"

	# so now we have the valid clip number and file, we can record into it:
	while True:
		button = GPIO.input(17)
		light_on()
		#start recording if the button is pressed
		if button == False:
			button = GPIO.input(17)
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
	
	#this will make sure the script returns to running again
	return True	

if __name__ == "__main__":
	os.chdir(AUDIODIR)	
	init()
	light_flash (0.5, 4)
	light_off()
	while main():
		time.sleep(.5)
