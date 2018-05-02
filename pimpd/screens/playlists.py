from screen import Screen
from widgets.textlist import TextList
from keyboardmanager import KeyboardManager
import time
import fonts


class PlayListsScreen(Screen):
    TIMEOUT = 10

    def __init__(self, screen_manager, keyboard_manager, client):
        super(PlayListsScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        self._current = None
        self._playlists = []

        font = fonts.DEFAULT_FONT_12
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
        if buttons_pressed == [KeyboardManager.CENTER] or buttons_pressed == [KeyboardManager.RIGHT]:
            self._current = self._tlist.selected
            if self._current is not None:
                pl = self._playlists[self._current]
                self._client.play_playlist(pl)
            self._screen_manager.pop_screen()
        elif buttons_pressed == [KeyboardManager.UP]:
            self._tlist.select_previous()
        elif buttons_pressed == [KeyboardManager.DOWN]:
            self._tlist.select_next()
        elif buttons_pressed == [KeyboardManager.LEFT]:
            self._screen_manager.pop_screen()

    def tick(self):
        super(PlayListsScreen, self).tick()
        if time.time() - self._last_update > PlayListsScreen.TIMEOUT:
            self._screen_manager.pop_screen()
