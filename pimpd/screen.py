from widget import Widget
from keyboardmanager import KeyboardManager
from collections import deque
import screenmanager
import threading


class Screen(object):
    def __init__(self, screen_manager, keyboard_manager):
        # type: (Screen, screenmanager.ScreenManager, KeyboardManager) -> None
        self._screen_manager = screen_manager
        self._keyboard_manager = keyboard_manager
        self._unprocessed_events = deque()
        self._lock = threading.Condition()
        self._active = False

    def widgets(self):
        # type: () -> [Widget]
        return []

    def activate(self):
        self._keyboard_manager.add_callback(self._keyboard_handler)
        self._active = True

    def deactivate(self):
        self._keyboard_manager.remove_callback(self._keyboard_handler)
        self._active = False

    def _keyboard_handler(self, buttons_pressed):
        self._lock.acquire()
        self._unprocessed_events.append(buttons_pressed)
        self._lock.release()
        return True

    def process_keyboard_events(self):
        # must periodically be called by the main thread to process pending events
        self._lock.acquire()
        for buttons in self._unprocessed_events:
            self.on_keyboard_event(buttons)
        self._unprocessed_events.clear()
        self._lock.release()

    def on_keyboard_event(self, buttons_pressed):
        # this function will always be called on the main thread
        pass

    def on_screen_off(self):
        pass

    def on_screen_on(self):
        pass

    def tick(self):
        pass
