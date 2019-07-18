
import pygame.mixer

pygame.mixer.init()
pygame.mixer.music.load("example_audio.wav")
pygame.mixer.music.set_volume(0.5)

pygame.mixer.music.play()

c=1

while pygame.mixer.music.get_busy() == True:
	print "Audio Playing" + str(c)
	c = c + 1	
	continue
