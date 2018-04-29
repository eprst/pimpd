from PIL import ImageFont

from screen import Screen
from tlist import TextList
from kbdmgr import KeyboardManager
import time


class PlayListsScreen(Screen):
    TIMEOUT = 10

    def __init__(self, screen_manager, keyboard_manager, client):
        super(PlayListsScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        self._current = None
        self._playlists = []

        font = ImageFont.truetype("DejaVuSans.ttf", 12)
        self._tlist = TextList((0, 0), (128, 64), font, 'No Play Lists')
        self._tlist.set_draw_border(True)

    def widgets(self):
        return [self._tlist]

    def activate(self):
        super(PlayListsScreen, self).activate()
        lists = self._client.listplaylists()
        self._playlists = [t['playlist'] for t in lists]
        self._tlist.set_items(self._playlists)
        if self._current is not None:
            self._tlist.set_selected(self._current)
        self._last_update = time.time()

    def on_keyboard_event(self, buttons_pressed):
        self._last_update = time.time()
        if buttons_pressed == [KeyboardManager.CENTER]:
            self._current = self._tlist.selected
            if self._current is not None:
                pl = self._playlists[self._current]
                print(pl)
                # todo: load playlist
                # todo: make a function in rmpd?
                # self._client.clear()
                # self._client.load(pl)
                # self._client.next()
            self._screen_manager.pop_screen()

    def timer_tick(self):
        super(PlayListsScreen, self).timer_tick()
        if time.time() - self._last_update > PlayListsScreen.TIMEOUT:
            self._screen_manager.pop_screen()
