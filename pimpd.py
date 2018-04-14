import RPi.GPIO as GPIO

import time
import socket

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from mpd import MPDClient

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Refresh rate
REFRESH_RATE = 0.05

# MPD config
MPD_SERVER = "192.168.1.154"
MPD_PORT = 6600
MPD_TIMEOUT = 10
MPD_IDLETIMEOUT = None

# GPIO setup
if ROTATE:
    L_pin = 23 
    R_pin = 27 
    U_pin = 22 
    D_pin = 17 
else:
    L_pin = 27 
    R_pin = 23 
    U_pin = 17 
    D_pin = 22 
C_pin = 4 
A_pin = 5 
B_pin = 6 

GPIO.setmode(GPIO.BCM) 
GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

RST = 24
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

font = ImageFont.truetype("abel-regular.ttf", 12)

mpd_connected = False
mpd = MPDClient(use_unicode=True)
mpd.timeout = MPD_TIMEOUT
mpd.idletimeout = MPD_IDLETIMEOUT

def scroll_text(draw, text, pos, offset, w = None)
    if not w:
        w = width - pos[0]
    ts = draw.textsize(text, font=font)
    

try:
    while 1:
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        
        try:
            if not mpd_connected:
                mpd.connect(MPD_SERVER, MPD_PORT)
                mpd_connected = True

            draw.text((0,10), mpd.mpd_version, font=font, fill=1)

        except socket.error, msg:
            mpd_connected = False
            print "MPD: %s\n" % msg
            draw.text((0,15), "MPD: %s" % msg, font=font, fill=1)
        
        if ROTATE:
            image = image.rotate(180)

        disp.image(image)
        disp.display()   
        time.sleep(REFRESH_RATE)

except KeyboardInterrupt: 
    disp.clear()
    disp.display()   
    GPIO.cleanup()
    if mpd_connected:
        mpd.close()
        mpd.disconnect()





#        draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
#         if GPIO.input(U_pin): # button is released
#             draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=0)  #Up
#         else: # button is pressed:
#             draw.polygon([(20, 20), (30, 2), (40, 20)], outline=255, fill=1)  #Up filled
# 
#         if GPIO.input(L_pin): # button is released
#             draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=0)  #left
#         else: # button is pressed:
#             draw.polygon([(0, 30), (18, 21), (18, 41)], outline=255, fill=1)  #left filled
# 
#         if GPIO.input(R_pin): # button is released
#             draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=0) #right
#         else: # button is pressed:
#             draw.polygon([(60, 30), (42, 21), (42, 41)], outline=255, fill=1) #right filled
# 
#         if GPIO.input(D_pin): # button is released
#             draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=0) #down
#         else: # button is pressed:
#             draw.polygon([(30, 60), (40, 42), (20, 42)], outline=255, fill=1) #down filled
# 
#         if GPIO.input(C_pin): # button is released
#             draw.rectangle((20, 22,40,40), outline=255, fill=0) #center 
#         else: # button is pressed:
#             draw.rectangle((20, 22,40,40), outline=255, fill=1) #center filled
# 
#         if GPIO.input(A_pin): # button is released
#             draw.ellipse((70,40,90,60), outline=255, fill=0) #A button
#         else: # button is pressed:
#             draw.ellipse((70,40,90,60), outline=255, fill=1) #A button filled
# 
#         if GPIO.input(B_pin): # button is released
#             draw.ellipse((100,20,120,40), outline=255, fill=0) #B button
#         else: # button is pressed:
#             draw.ellipse((100,20,120,40), outline=255, fill=1) #B button filled
# 
#         if not GPIO.input(A_pin) and not GPIO.input(B_pin) and not GPIO.input(C_pin):
#             catImage = Image.open('happycat_oled_64.ppm').convert('1')
#             disp.image(catImage)
#         else:
#             # Display image.
#             disp.image(image)
