import screen
from collections import deque
import time
from PIL import Image
from PIL import ImageDraw
import Adafruit_SSD1306

class ScreenManager(object):
    _screen = None  # type: screen.Screen

    def __init__(self, rotate, refresh_rate):
        self._screen = None
        self._prev_screens = deque()
        self._rotate = rotate
        self._refresh_rate = refresh_rate

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

    def run(self):
        # starts the main loop in the current thread
        RST = 24
        disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
        disp.begin()
        disp.clear()
        disp.display()

        width = disp.width
        height = disp.height
        image = Image.new('1', (width, height))

        screen = self._screen
        if self._screen is None:
            widgets = []
        else:
            widgets = screen.widgets()

        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        try:
            while True:
                if screen == self._screen:
                    global_update = False
                else:
                    global_update = True
                    draw.rectangle((0, 0, width, height), outline=0, fill=0)
                    screen = self._screen
                    if self._screen is None:
                        widgets = []
                    else:
                        widgets = screen.widgets()

                screen.process_keyboard_events()

                have_updates = False

                for w in widgets:
                    w.tick()
                    if global_update or w.need_refresh():
                        w.refresh(image, draw)
                        have_updates = True

                if have_updates:
                    if self._rotate:
                        disp.image(image.transpose(Image.ROTATE_180))
                    else:
                        disp.image(image)
                    disp.display()

                time.sleep(self._refresh_rate)
        except KeyboardInterrupt:
            disp.clear()
            disp.display()
