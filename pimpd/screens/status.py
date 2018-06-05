import threading
import time

import fonts
from screen import Screen
from widgets.scrollingtext import ScrollingText


class StatusScreen(Screen):
    def __init__(self, screen_manager, keyboard_manager, client):
        super(StatusScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        font = fonts.DEFAULT_FONT_12
        self._label = ScrollingText((0, 5), (125, 15), font, u'Status')
        self._status = ScrollingText((0, 25), (125, 15), font, u'')
        self._failure = ScrollingText((0, 45), (125, 15), font, u'')

        self._active_mutex = threading.Condition()
        self._thread_started_cond = threading.Condition()

        thread = threading.Thread(target=self._poll)
        thread.setDaemon(True)
        self._thread_started_cond.acquire()
        thread.start()
        self._thread_started_cond.wait()
        self._thread_started_cond.release()

    def activate(self):
        Screen.activate(self)
        self._active_mutex.acquire()
        self._active_mutex.notifyAll()
        self._active_mutex.release()

    def _poll(self):
        while True:
            self._active_mutex.acquire()
            self._thread_started_cond.acquire()
            self._thread_started_cond.notifyAll()
            self._thread_started_cond.release()
            self._active_mutex.wait()
            self._active_mutex.release()
            while self._active:
                self._status.set_text(self._client.connection_status)
                lf = self._client.last_connection_failure
                if lf is None:
                    self._failure.set_text(u'')
                else:
                    self._failure.set_text(lf)

                if self._client.connected:
                    self._screen_manager.pop_screen()
                    break

                time.sleep(2)

    def widgets(self):
        return [self._label, self._status, self._failure]
