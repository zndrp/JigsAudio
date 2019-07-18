#/usr/bin/env python

import os
# import pyaudio
# import pygame.mixer
import glob

AUDIODIR = "/home/pi/audiorecordings"


os.chdir(AUDIODIR)
puz_id = raw_input("What's the id. of the puzzle piece? (scan the piece): ")

#identify the clip
clip_file = puz_id + "-1.wav"


files = glob.glob(puz_id + "*.wav")

for file in files:
	if file == clip_file:
		play_piece(clip_file)

	else:
		record()

if not:
	print "No clips found on this piece."
	break



def play_piece(clip_file)
	#put the green light on

	pygame.mixer.init()
	pygame.mixer.music.load(clip_file)
	pygame.mixer.music.set_volume(0.5)

	pygame.mixer.music.play()

	while pygame.mixer.music.get_busy() == True:
		print "Playing Clip: " + clip_file
		#allow the play button to stop playing the clip
		continue

	#turn green light off when finished
	pring "Clip finished"
	record()