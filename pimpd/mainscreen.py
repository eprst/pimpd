import time
from select import select

import mpd
from PIL import ImageFont

from pbar import ProgressBar
from playing import PlayingWidget
from screen import Screen
from stext import ScrollingText
from kbdmgr import KeyboardManager


class MainScreen(Screen):
    UPDATE_EVERY = 2

    def __init__(self, screen_manager, keyboard_manager, client, status_screen, volmgr):
        super(MainScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        self._status_screen = status_screen
        self._volmgr = volmgr

        font = ImageFont.truetype("DejaVuSans.ttf", 14)

        self._status = PlayingWidget((0, 0), (9, 9))
        self._seekbar = ProgressBar((24, 1), (128 - 24, 7), 100)

        self._artist = ScrollingText((0, 12), (128, 16), font, '')

        self._title = ScrollingText((0, 32), (128, 16), font, '')

        # self._volume_label = ScrollingText((-2, 50), (50, 13), font, ' Volume')
        # self._volume_label.set_draw_border(True)
        # self._volume = ProgressBar((55, 54), (128 - 55, 7), 100)

        self._volume = ProgressBar((0, 54), (128, 7), 100)

        client.add_connected_callback(self._connected)
        self._last_update = time.time()

    def widgets(self):
        return [self._status, self._seekbar, self._artist, self._title,
                # self._volume_label, self._volume]
                self._volume]

    def _connected(self):
        self._update_status()
        self._client.send_idle()

    def _idle_update_status(self):
        try:
            self._client.fetch_idle()
        except mpd.base.PendingCommandError:
            pass

        self._update_status()
        self._client.send_idle()  # continue idling

    def _update_status(self):
        cs = self._client.currentsong()

        artist = cs.get('artist', 'Unknown Artist')
        self._artist.set_text(artist)

        title = cs.get('title', None)
        file = cs.get('file', None)
        if title is not None:
            self._title.set_text(title)
        elif file is not None:
            self._title.set_text(file)
        else:
            self._title.set_text('Unknown Title')

        st = self._client.status()

        state = st.get('state', 'stop')  # play/stop/pause
        if state == 'play':
            self._status.set_status(PlayingWidget.PLAYING)
        elif state == 'stop':
            self._status.set_status(PlayingWidget.STOPPED)
        elif state == 'pause':
            self._status.set_status(PlayingWidget.PAUSED)

        elapsed = float(st.get('elapsed', 0.0))
        if elapsed == 0.0:
            elapsed = float(st.get('time', 0.0))
        duration = float(st.get('duration', 0.0))
        if duration > 0:
            self._seekbar.set_value(elapsed * 100 / duration)
        else:
            self._seekbar.set_value(0)

        volume = self._volmgr.volume
        self._volume.set_value(volume)

        self._last_update = time.time()

    def timer_tick(self):
        if self._client.connected:
            force_update = time.time() - self._last_update > MainScreen.UPDATE_EVERY
            if force_update:
                try:
                    self._client.noidle()
                except mpd.base.CommandError:
                    pass
                self._update_status()
            elif select([self._client], [], [], 0)[0]:
                self._idle_update_status()
        else:
            self._screen_manager.set_screen(self._status_screen)

    def on_keyboard_event(self, buttons_pressed):
        if buttons_pressed == [KeyboardManager.LEFT]:
            volume = self._volmgr.volume
            volume = max(0, volume - 5)
            self._volmgr.set_volume(volume)
        elif buttons_pressed == [KeyboardManager.RIGHT]:
            volume = self._volmgr.volume
            volume = min(100, volume + 5)
            self._volmgr.set_volume(volume)
        elif buttons_pressed == [KeyboardManager.CENTER]:
            status = self._status.status
            if status == PlayingWidget.PLAYING:
                self._client.pause(1)
                self._status.set_status(PlayingWidget.PAUSED)
            elif status == PlayingWidget.PAUSED:
                self._client.pause(0)
                self._status.set_status(PlayingWidget.PLAYING)
