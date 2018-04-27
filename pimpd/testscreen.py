# -*- coding: utf-8 -*-
from stext import ScrollingText
from pbar import ProgressBar
from tlist import TextList
from kbdmgr import KeyboardManager
from screen import Screen
from PIL import ImageFont


class WidgetsTestScreen(Screen):
    def __init__(self, screen_manager, keyboard_manager):
        super(WidgetsTestScreen, self).__init__(screen_manager, keyboard_manager)
        font = ImageFont.truetype("DejaVuSans.ttf", 12)
        self._val = 0
        self._pbar = ProgressBar((0, 30), (40, 10), 100)
        self._tlist = TextList((45, 5), (80, 55), font, "no playlists")
        self._tlist.set_draw_border(True)
        self._tlist.set_items(["one one one one", "two two two two", "three three three three", "four", "five"])
        self._stext = ScrollingText((0, 0), (40, 20), font, u'Hello::Привет!')

    def on_keyboard_event(self, buttons_pressed):
        if buttons_pressed == [KeyboardManager.UP]:
            self._tlist.select_previous()
        elif buttons_pressed == [KeyboardManager.DOWN]:
            self._tlist.select_next()
        elif buttons_pressed == [KeyboardManager.LEFT]:
            val = max(0, self._val - 5)
            self._pbar.set_value(val)
        elif buttons_pressed == [KeyboardManager.RIGHT]:
            val = min(100, self._val + 5)
            self._pbar.set_value(val)
        elif buttons_pressed == [KeyboardManager.CENTER]:
            print("selected: %s" % str(self._tlist.selected))

    def widgets(self):
        return [self._pbar, self._tlist, self._stext]
