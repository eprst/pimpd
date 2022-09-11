import asyncio

from widget import Widget
from keyboardmanager import KeyboardManager


class Screen(object):
    # can't specify screenmanager type here due to circular import
    def __init__(self, screen_manager, keyboard_manager: KeyboardManager) -> None:
        self._screen_manager = screen_manager
        self._keyboard_manager = keyboard_manager
        # self._update_task: asyncio.Task | None = None # python 3.10
        self._update_task: asyncio.Task = None

    def widgets(self) -> list[Widget]:
        return []

    async def activate(self):
        if self.active():
            raise "screen already activated!"
        self._update_task = asyncio.create_task(self._update_loop())
        self._keyboard_manager.add_callback(self.on_keyboard_event)
        for w in self.widgets():
            w.start()

    def deactivate(self):
        if not self.active():
            raise "screen already deactivated!"
        self._update_task.cancel()
        self._update_task = None
        self._keyboard_manager.remove_callback(self.on_keyboard_event)
        for w in self.widgets():
            w.stop()

    def active(self) -> bool:
        return self._update_task is not None

    async def on_keyboard_event(self, buttons_pressed: list[int]) -> bool:
        return False

    def on_screen_off(self):
        pass

    def on_screen_on(self):
        pass

    async def _update_loop(self):
        pass
