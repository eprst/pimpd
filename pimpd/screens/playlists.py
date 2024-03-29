import asyncio

from screen import Screen
from widgets.textlist import TextList
from keyboardmanager import KeyboardManager
import time
import fonts
import logging


class PlayListsScreen(Screen):
    TIMEOUT = 10

    def __init__(self, screen_manager, keyboard_manager, client):
        super(PlayListsScreen, self).__init__(screen_manager, keyboard_manager)
        self._last_update = None
        self._client = client
        self._current = None
        self._playlists = []

        font = fonts.DEFAULT_FONT_12
        self._tlist = TextList((0, 0), (128, 64), font, 'No Play Lists')
        self._tlist.set_draw_border(True)

    def widgets(self):
        return [self._tlist]

    async def activate(self):
        await super(PlayListsScreen, self).activate()
        if self._client.connected:
            lists = await self._client.listplaylists()
            self._playlists = [t['playlist'] for t in lists]
            self._tlist.set_items(self._playlists)
            if self._current is not None:
                self._tlist.set_selected(self._current)
            self._last_update = time.time()
        else:
            logging.info("Can't load playlists: not connected yet")

    async def on_keyboard_event(self, buttons_pressed: list[int]) -> bool:
        if buttons_pressed == [KeyboardManager.CENTER] or buttons_pressed == [KeyboardManager.RIGHT]:
            self._current = self._tlist.selected
            if self._current is not None:
                pl = self._playlists[self._current]
                await self._client.play_playlist(pl)
            await self._screen_manager.pop_screen()
        elif buttons_pressed == [KeyboardManager.UP]:
            self._tlist.select_previous()
        elif buttons_pressed == [KeyboardManager.DOWN]:
            self._tlist.select_next()
        elif buttons_pressed == [KeyboardManager.LEFT]:
            await self._screen_manager.pop_screen()
        else:
            return False

        self._last_update = time.time()
        return True

    async def _update_loop(self):
        try:
            while True:
                await asyncio.sleep(1)
                if self._last_update is not None and time.time() - self._last_update > PlayListsScreen.TIMEOUT:
                    await self._screen_manager.pop_screen()
        except asyncio.CancelledError:
            pass
