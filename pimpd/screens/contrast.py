from widget import Widget
from widgets.progressbar import ProgressBar
from screen import Screen
from widgets.scrollingtext import ScrollingText
from keyboardmanager import KeyboardManager
import fonts
import logging


class ContrastScreen(Screen):
    def __init__(self, screen_manager, keyboard_manager, disp):
        super(ContrastScreen, self).__init__(screen_manager, keyboard_manager)
        self._disp = disp
        self._contrast = 0xCF  # initial value from SSD1306.py
        self._pbar = ProgressBar((0, 25), (128, 14), 255)
        self._pbar.set_value(0xCF)
        font = fonts.DEFAULT_FONT_12
        self._label = ScrollingText((25, 5), (100, 15), font, 'Contrast')

    async def on_keyboard_event(self, buttons_pressed: list[int]) -> bool:
        if buttons_pressed == [KeyboardManager.LEFT]:
            self._contrast = max(0, self._contrast - 5)
        elif buttons_pressed == [KeyboardManager.RIGHT]:
            self._contrast = min(255, self._contrast + 5)
        elif buttons_pressed == [KeyboardManager.CENTER]:
            await self._screen_manager.pop_screen()
        else:
            return False

        logging.debug("setting contrast to %d", self._contrast)
        self._disp.set_contrast(self._contrast)
        self._pbar.set_value(self._contrast)
        return True

    def widgets(self) -> list[Widget]:
        return [self._pbar, self._label]
