# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO

import time
import socket
import threading

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from stext import ScrollingText
from pbar import ProgressBar
from tlist import TextList
from kbdmgr import KeyboardManager

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Refresh rate
REFRESH_RATE = 0.01

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

font = ImageFont.truetype("DejaVuSans.ttf", 12)
stext = ScrollingText((0, 0), (40, 20), font, u'Hello::Привет!')
# stext.set_draw_border(True)
stext.set_invert(True)
pbar = ProgressBar((0, 30), (40, 10), 100)
val = 0
tlist = TextList((45, 5), (80, 55), font, "no playlists")
tlist.set_draw_border(True)
#tlist.set_items(["one one one one","two two two two","three three three three", "four", "five"])
#tlist.set_items(["one one one one","two two two two","three three three three", "four"])
#tlist.set_items(["one one one one","two two two two","three three three three"])
#tlist.set_items(["one one one one","two two two two"])
#tlist.set_items(["one one one one"])
tlist.set_items([])

lock = threading.Condition()

kmgr = KeyboardManager()

def up_down_cb(channel):
    lock.acquire()
    if channel == U_pin:
        tlist.select_previous()
    elif channel == D_pin:
        tlist.select_next()
    elif channel == C_pin:
        print("selected: %s" % str(tlist.selected))
    lock.release()

try:
    GPIO.add_event_detect(U_pin, GPIO.RISING, callback=up_down_cb, bouncetime=200)
    GPIO.add_event_detect(D_pin, GPIO.RISING, callback=up_down_cb, bouncetime=200)
    GPIO.add_event_detect(C_pin, GPIO.RISING, callback=up_down_cb, bouncetime=200)
    while 1:
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if not GPIO.input(L_pin):
            val = max(0, val - 5)
        if not GPIO.input(R_pin):
            val = min(100, val + 5)

        pbar.set_value(val)

        stext.refresh(image, draw)
        pbar.refresh(image, draw)
        lock.acquire()
        tlist.refresh(image, draw)
        lock.release()

        if ROTATE:
            image = image.rotate(180)

        disp.image(image)
        disp.display()
        time.sleep(REFRESH_RATE)

except KeyboardInterrupt:
    disp.clear()
    disp.display()
    GPIO.cleanup()
