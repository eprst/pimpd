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

    def activate(self):
        Screen.activate(self)
        thread = threading.Thread(target=self._poll)
        thread.setDaemon(True)
        thread.start()

    def _poll(self):
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
