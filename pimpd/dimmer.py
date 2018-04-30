import threading
import time
from screenmanager import ScreenManager
from kbdmgr import KeyboardManager


class Dimmer(object):
    def __init__(self, screen_manager, keyboard_manager, dim_after, off_after, pass_through_buttons):
        self._dim_after = dim_after
        self._off_after = off_after
        self._smgr = screen_manager
        self._pass_through_buttons = pass_through_buttons
        self._last_activity = time.time()

        self._dimmed = False
        self._off = False

        self._lock = threading.Condition()

        keyboard_manager.add_callback(self._on_kbd)

        thread = threading.Thread(target=self._check)
        thread.setDaemon(True)
        thread.start()

    def _check(self):
        while True:
            time.sleep(1)
            sla = time.time() - self._last_activity

            if self._dim_after is not None and sla > self._dim_after:
                self._smgr.dim()
                self._dimmed = True

            if self._off_after is not None and sla > self._off_after:
                self._smgr.screen_off()
                self._off = True
                self._lock.acquire()
                self._lock.wait()
                self._lock.release()

    def _on_kbd(self, buttons):
        self._last_activity = time.time()
        processed = False
        if self._off:
            self._smgr.screen_on()
            self._off = False
            processed = len(buttons) == 1 and buttons[0] not in self._pass_through_buttons
        if self._dimmed:
            self._smgr.undim()
            self._dimmed = False
            self._lock.acquire()
            self._lock.notifyAll()
            self._lock.release()
            processed = len(buttons) == 1 and buttons[0] not in self._pass_through_buttons
        return processed
