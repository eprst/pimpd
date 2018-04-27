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
from smgr import ScreenManager
from testscreen import WidgetsTestScreen

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Refresh rate
REFRESH_RATE = 0.1

kmgr = KeyboardManager(ROTATE)
smgr = ScreenManager(ROTATE, REFRESH_RATE)
testscreen = WidgetsTestScreen(smgr, kmgr)

smgr.set_screen(testscreen)

smgr.run() # main loop

kmgr.stop()

#
# # GPIO setup
# if ROTATE:
#     L_pin = 23
#     R_pin = 27
#     U_pin = 22
#     D_pin = 17
# else:
#     L_pin = 27
#     R_pin = 23
#     U_pin = 17
#     D_pin = 22
# C_pin = 4
# A_pin = 5
# B_pin = 6
#
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(L_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(R_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(U_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(D_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#
# RST = 24
# DC = 23
# SPI_PORT = 0
# SPI_DEVICE = 0
#
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
#
# disp.begin()
# disp.clear()
# disp.display()
#
# width = disp.width
# height = disp.height
# image = Image.new('1', (width, height))
#
# font = ImageFont.truetype("DejaVuSans.ttf", 12)
# stext = ScrollingText((0, 0), (40, 20), font, u'Hello::Привет!')
# # stext.set_draw_border(True)
# stext.set_invert(True)
# pbar = ProgressBar((0, 30), (40, 10), 100)
# val = 0
# tlist = TextList((45, 5), (80, 55), font, "no playlists")
# tlist.set_draw_border(True)
# tlist.set_items(["one one one one","two two two two","three three three three", "four", "five"])
# #tlist.set_items(["one one one one","two two two two","three three three three", "four"])
# #tlist.set_items(["one one one one","two two two two","three three three three"])
# #tlist.set_items(["one one one one","two two two two"])
# #tlist.set_items(["one one one one"])
# #tlist.set_items([])
#
# lock = threading.Condition()
#
#
# def buttons_callback(buttons):
#     global val
#     lock.acquire()
#     if buttons == [KeyboardManager.UP]:
#         tlist.select_previous()
#     elif buttons == [KeyboardManager.DOWN]:
#         tlist.select_next()
#     elif buttons == [KeyboardManager.LEFT]:
#         val = max(0, val - 5)
#         pbar.set_value(val)
#     elif buttons == [KeyboardManager.RIGHT]:
#         val = min(100, val + 5)
#         pbar.set_value(val)
#     elif buttons == [KeyboardManager.CENTER]:
#         print("selected: %s" % str(tlist.selected))
#     lock.release()
#
# kmgr = KeyboardManager(ROTATE)
# kmgr.add_callback(callback = buttons_callback)
#
# try:
#     widgets = [stext, pbar, tlist]
#     draw = ImageDraw.Draw(image)
#     draw.rectangle((0, 0, width, height), outline=0, fill=0)
#
#     while 1:
#         have_updates = False
#         for w in widgets:
#             w.tick()
#             if w.need_refresh():
#                 lock.acquire()
#                 w.refresh(image, draw)
#                 lock.release()
#                 have_updates = True
#
#         if have_updates:
#             if ROTATE:
#                 disp.image(image.transpose(Image.ROTATE_180))
#             else:
#                 disp.image(image)
#             disp.display()
#
#         time.sleep(REFRESH_RATE)
#
#         #todo: implement display sleeping/dimming
#
# except KeyboardInterrupt:
#     kmgr.stop()
#     disp.clear()
#     disp.display()
#     GPIO.cleanup()
