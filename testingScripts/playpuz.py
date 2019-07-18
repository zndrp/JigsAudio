import signal
import time
from sys import exit
import unicornhat as unicorn
from PIL import Image
import pygame.mixer

#This is the directory the audio files are stored in 
AUDIODIR = "/home/pi/audiorecordings"


unicorn.set_layout(unicorn.HAT)
unicorn.rotation(270)
unicorn.brightness(.5)

img = Image.open('hatimages/playing.png')


pygame.mixer.init()
pygame.mixer.music.load("example_audio.wav")
pygame.mixer.music.set_volume(0.5)

pygame.mixer.music.play()

for o_x in range(int(img.size[0]/8)):
    for o_y in range(int(img.size[1]/8)):

        for x in range(8):
            for y in range(8):
                pixel = img.getpixel(((o_x*8)+y,(o_y*8)+x))
                print(pixel)
                r, g, b = int(pixel[0]),int(pixel[1]),int(pixel[2])
                unicorn.set_pixel(x, y, r, g, b)
            unicorn.show()
            time.sleep(.5)

while pygame.mixer.music.get_busy() == True:	
	continue
