import asyncio
import logging
import traceback
from collections import deque

import adafruit_ssd1306
import board
import busio
import typing
from PIL import Image
from PIL import ImageDraw

import screen


class ScreenManager(object):
    _screen: typing.Union[screen.Screen, None] = None

    def __init__(self, rotate, refresh_rate):
        self._screen = None
        self._prev_screens = deque()
        self._rotate = rotate
        self._refresh_rate = refresh_rate
        self._screen_off = False
        self._redraw = False
        self._kill = False
        i2c = busio.I2C(board.SCL, board.SDA)
        self._disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        # RST = 24
        # self._disp = adafruit_ssd1306.SSD1306_128_64(rst=RST)

    @property
    def display(self):
        return self._disp

    def is_screen_off(self):
        return self._screen_off

    async def set_screen(self, _screen):
        if self._screen is not None:
            self._prev_screens.append(self._screen)
        await self._set_screen(_screen)

    async def pop_screen(self):
        # go to previous screen
        if len(self._prev_screens) == 0:
            await self._set_screen(None)
        else:
            await self._set_screen(self._prev_screens.pop())

    def reset_screen(self, screen):
        self._prev_screens.clear()
        self._set_screen(screen)

    async def _set_screen(self, _screen: typing.Union[screen.Screen, None]):
        if self._screen is not None:
            self._screen.deactivate()
        self._screen = _screen
        if self._screen is not None:
            await self._screen.activate()

    def dim(self):
        self._disp.contrast(0)

    def undim(self):
        self._disp.contrast(0xCF)  # or 0x9F

    def screen_off(self):
        self._screen_off = True
        self._redraw = True
        if self._screen is not None:
            self._screen.on_screen_off()

    def screen_on(self):
        self._screen_off = False
        self._redraw = True
        if self._screen is not None:
            self._screen.on_screen_on()

    async def run(self):
        # self._disp.begin()
        self._disp.fill(0)
        self._disp.show()

        width = self._disp.width
        height = self._disp.height
        image = Image.new('1', (width, height))

        current_screen = self._screen
        if current_screen is None:
            widgets = []
        else:
            widgets = current_screen.widgets()

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        while True:
            try:
                global_update = self._redraw or current_screen != self._screen
                self._redraw = False
                have_updates = global_update

                if self._screen_off:
                    draw.rectangle((0, 0, width, height), outline=0, fill=0)
                else:
                    if global_update:
                        draw.rectangle((0, 0, width, height), outline=0, fill=0)
                        current_screen = self._screen
                        if current_screen is None:
                            widgets = []
                        else:
                            widgets = current_screen.widgets()

                    for w in widgets:
                        if global_update or w.need_refresh():
                            w.refresh(image, draw)
                            have_updates = True

                if have_updates:
                    if self._rotate:
                        self._disp.image(image.transpose(Image.ROTATE_180))
                    else:
                        self._disp.image(image)
                    self._disp.show()

                await asyncio.sleep(self._refresh_rate)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(e)
                logging.error(traceback.format_exc())

        self._disp.fill(0)
        self._disp.show()
