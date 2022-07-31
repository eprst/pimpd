import screen
from collections import deque
import time
import traceback
import logging
from PIL import Image
from PIL import ImageDraw
import board
import busio
import adafruit_ssd1306


class ScreenManager(object):
    _screen = None  # type: screen.Screen

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

    def shutdown(self):
        self._kill = True

    @property
    def display(self):
        return self._disp

    def is_screen_off(self):
        return self._screen_off

    def set_screen(self, screen):
        if self._screen is not None:
            self._prev_screens.append(self._screen)
        self._set_screen(screen)

    def pop_screen(self):
        # go to previous screen
        if len(self._prev_screens) == 0:
            self._set_screen(None)
        else:
            self._set_screen(self._prev_screens.pop())

    def reset_screen(self, screen):
        self._prev_screens.clear()
        self._set_screen(screen)

    def _set_screen(self, screen):
        if self._screen is not None:
            self._screen.deactivate()
        self._screen = screen
        if self._screen is not None:
            self._screen.activate()

    def dim(self):
        # disp.dim is broken, see https://github.com/adafruit/Adafruit_Python_SSD1306/issues/23
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

    def run(self):
        # starts the main loop in the current thread
        # self._disp.begin()
        self._disp.fill(0)
        self._disp.show()

        width = self._disp.width
        height = self._disp.height
        image = Image.new('1', (width, height))

        screen = self._screen
        if screen is None:
            widgets = []
        else:
            widgets = screen.widgets()

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        while not self._kill:
            try:
                if screen is not None:
                    screen.tick()

                global_update = self._redraw or screen != self._screen
                self._redraw = False
                have_updates = global_update

                if self._screen_off:
                    draw.rectangle((0, 0, width, height), outline=0, fill=0)
                else:
                    if global_update:
                        draw.rectangle((0, 0, width, height), outline=0, fill=0)
                        screen = self._screen
                        if screen is None:
                            widgets = []
                        else:
                            widgets = screen.widgets()

                    if screen is not None:
                        screen.process_keyboard_events()

                    for w in widgets:
                        w.tick()
                        if global_update or w.need_refresh():
                            w.refresh(image, draw)
                            have_updates = True

                if have_updates:
                    if self._rotate:
                        self._disp.image(image.transpose(Image.ROTATE_180))
                    else:
                        self._disp.image(image)
                    self._disp.show()

                time.sleep(self._refresh_rate)
            except Exception as e:
                logging.error(repr(e))
                logging.error(traceback.format_exc())

        self._disp.fill(0)
        self._disp.show()
