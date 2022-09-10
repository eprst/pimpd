import asyncio
import fonts
import keyboardmanager
import reconnectingclient
import screenmanager
from screen import Screen
from widgets.scrollingtext import ScrollingText


class StatusScreen(Screen):
    def __init__(self,
                 screen_manager: screenmanager.ScreenManager,
                 keyboard_manager: keyboardmanager.KeyboardManager,
                 client: reconnectingclient.ReconnectingClient):
        super(StatusScreen, self).__init__(screen_manager, keyboard_manager)
        self._screen_manager = screen_manager
        self._client = client
        font = fonts.DEFAULT_FONT_12
        self._label = ScrollingText((0, 5), (125, 15), font, u'Status')
        self._status = ScrollingText((0, 25), (125, 15), font, u'')
        self._failure = ScrollingText((0, 45), (125, 15), font, u'')

    async def activate(self):
        await super().activate()
        await self._client.add_connected_callback(self._connected)

    def deactivate(self):
        super().deactivate()
        self._client.remove_connected_callback(self._connected)

    async def _connected(self):
        await self._screen_manager.pop_screen()  # this should cancel the update loop

    async def _update_loop(self):
        try:
            while True:
                self._status.set_text(self._client.connection_status)
                lf = self._client.last_connection_failure
                if lf is None:
                    self._failure.set_text(u'')
                else:
                    self._failure.set_text(lf)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def widgets(self):
        return [self._label, self._status, self._failure]
