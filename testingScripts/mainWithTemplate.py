#/usr/bin/env python
import os
import pyaudio
import wave
import sys
import RPi.GPIO as GPIO
import time
import glob
#import pygame
import subprocess
#import signal

#GLOBALS HERE:
#this is where the audio is going to be recorded to:
AUDIODIR = "/home/pi/audiorecordings/"
scan_time = None
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
light_status = False


#do this before setting doing anything else.
def init():
	#setup GPIO Pins
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	GPIO.setup(18,GPIO.OUT) #this is the red LED
	GPIO.setup(17,GPIO.IN, pull_up_down=GPIO.PUD_UP) #this is the red button
	GPIO.setup(23,GPIO.OUT) #this is the green LED
	GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)
 	#this is the green button

	print "JigsAudio v3.0"

 	if os.path.isdir(AUDIODIR):
 		print "Audio Directory exists. Audio directory setup correctly"

 	if not os.path.isdir(AUDIODIR):
 		print "No Directory for Audio exists - exit the script and type: 'mkdir /home/pi/audiorecordings/'"

def captureAudio(file):
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
		global light_status
			
		if i % 24  == 0:
			if light_status:
				light("red", "off")
				light_status = False
			else:
				light("red", "on")
				light_status = True

		if GPIO.input(17) == False and i > 200:
			break


	print "finished recording as: " + file
 	stop_rec(stream, audio, file, frames)


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

def light(colour, on_off):
	if colour == "red" and on_off == "on":
		GPIO.output(18,GPIO.HIGH)

	if colour == "green" and on_off == "on":
		GPIO.output(23,GPIO.HIGH)

	if colour == "red" and on_off == "off":
		GPIO.output(18,GPIO.LOW)

	if colour == "green" and on_off == "off":
		GPIO.output(23,GPIO.LOW)

	if colour == "both" and on_off == "on":
		GPIO.output(23,GPIO.LOW)

	if colour == "both" and on_off == "off":
		GPIO.output(23,GPIO.LOW)

	else:
		return

def light_flash(flashfrq, flashno):
	flashes = 0
	while flashes < flashno:
		GPIO.output(18,GPIO.HIGH)
		GPIO.output(23,GPIO.HIGH)
		time.sleep(flashfrq)
		GPIO.output(18,GPIO.LOW)
		GPIO.output(23,GPIO.LOW)
		time.sleep(flashfrq)
		flashes = flashes + 1

def main():

	while True:
		#grab the puzzle piece ID, and format it into an mp3 file
		current_time = time.time()
		print current_time
		puz_id = raw_input("What's the number of the puzzle piece? (scan the piece): ")

		if puz_id == "":
			puz_id = "NoUserInput"
		
		time_scanned = time.time()
		print time_scanned

		#this will look for the last scan. If the scan was made within 1 second of the scipt being ready, they will be discarded.
		diff_time = time_scanned - current_time
		print diff_time

		if diff_time > 1:
			break

	print puz_id
	clipno = 1
	prev_rec = False

	#It's always ready to make a recording
	#is there already audio? Find a filename to use:
	while os.path.exists(puz_id + "-" + str(clipno) + ".wav"):
		clipno = clipno + 1
		prev_rec = True
	
	puz_file = puz_id + "-" + str(clipno) + ".wav"

	#take the time the puzzle was scanned to later compare (to look for errors of multiple scans)
	scan_time = time.time()

	print "ready to record"
	light("red", "on")

	if prev_rec:
		print "ready to play"
		light("green", "on")

	while True:
		green_button = GPIO.input(27)
		red_button = GPIO.input(17)

		if not red_button:
			print puz_file
			record(puz_file)
			break

		if not green_button and prev_rec:
			light("red","off")
			play_piece(str(puz_id + "-1.wav"))
			break

		current_time = time.time()
		time_since_scan = current_time - scan_time

		if time_since_scan > 10:
			print "Button Not Pressed - Timed Out"
			light("red","off")
			break
	
	return True

def record(puz_id):
	
	file = AUDIODIR + puz_id
	print file
	captureAudio(file)
	print "sound recordeded to: " + puz_id
	flashfrq = 0.1
	flashno = 6
	light_flash(flashfrq, flashno)

	#this will make sure the script returns to running again
	return True

p = None

def play_piece(audio_path):
	p = subprocess.Popen("aplay " + audio_path, shell=True)
	
	light("green","on")
	print "playing"
	time.sleep(2)
	while True:
#		print p.poll()
 		if p.poll() is not None or not GPIO.input(27):
#			print 'hejsan, we got i to kill'
#			p.send_signal(signal)
#			s.killpg(os.getpgid(p.pid), signal.SIGTERM)	
#			p = None	
			os.system("killall aplay")
			#put the light flashing script here
			break

	light("green", "off")
	print "Clip finished"
	
def webpage_builder
	#last recording
	last_use = time.strftime("%b %d %Y %H:%M:%S")

	#number of recordings
	no_files = len([name for name in os.listdir(AUDIODIR) if os.path.isfile(os.path.join(AUDIODIR, name))])


	template(last_use, no_files)


if __name__ == "__main__":
	os.chdir(AUDIODIR)	
	init()
	light_flash (0.3, 6)
	light("both", "off")
	while main():
		time.sleep(.5)
