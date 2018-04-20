import RPi.GPIO as GPIO

import time
import socket

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from stext import ScrollingText

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Refresh rate
REFRESH_RATE = 0.1

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

font = ImageFont.truetype("../abel-regular.ttf", 12)
stext = ScrollingText((10,10), (40,20), font, "Hello, world!!!")

try:
    while 1:
        draw = ImageDraw.Draw(image)
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        
        stext.refresh(image, draw)
        
        if ROTATE:
            image = image.rotate(180)

        disp.image(image)
        disp.display()   
        time.sleep(REFRESH_RATE)

except KeyboardInterrupt: 
    disp.clear()
    disp.display()   
    GPIO.cleanup()