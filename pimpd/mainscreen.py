# -*- coding: utf-8 -*-
import time
from select import select

import mpd
from PIL import ImageFont

from pbar import ProgressBar
from playing import PlayingWidget
from screen import Screen
from stext import ScrollingText
from kbdmgr import KeyboardManager
from playlists import PlayListsScreen


class MainScreen(Screen):
    # refresh on updates from server or every <REFRESH_RATE> seconds
    REFRESH_RATE = 5
    # playlist to start on pressing 'A' button
    A_PLAYLIST = u'Дождь'

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

        self._play_list_screen = PlayListsScreen(screen_manager, keyboard_manager, client)

        self._last_update = time.time()

    def widgets(self):
        return [self._status, self._seekbar, self._artist, self._title,
                # self._volume_label, self._volume]
                self._volume]

    def activate(self):
        super(MainScreen, self).activate()
        # this will immediately trigger _connected if already connected
        self._client.add_connected_callback(self._connected)

    def deactivate(self):
        super(MainScreen, self).deactivate()
        self._client.remove_connected_callback(self._connected)
        # print("deactivate: noidle")
        self._stop_idle()

    def _connected(self):
        self._update_status()
        # print("_connected: idle")
        self._client.send_idle()

    def _idle_update_status(self):
        try:
            self._client.fetch_idle()
        except mpd.base.PendingCommandError:
            pass

        self._update_status()
        # print("_idle_update_status: idle")
        self._client.send_idle()  # continue idling

    def _update_status(self):
        st = self._client.status()
        cs = self._client.currentsong()

        state = st.get('state', 'stop')  # play/stop/pause
        if state == 'play':
            self._status.set_status(PlayingWidget.PLAYING)
        elif state == 'stop':
            self._status.set_status(PlayingWidget.STOPPED)
        elif state == 'pause':
            self._status.set_status(PlayingWidget.PAUSED)

        if state == 'stop':
            self._artist.set_text('<stopped>')
            self._title.set_text('')
        else:
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

    def _stop_idle(self):
        try:
            self._client.noidle()
        except mpd.base.CommandError:
            pass

    def _force_update(self):
        # print("_force_update: noidle")
        self._stop_idle()
        self._update_status()
        # print("_force_update: idle")
        self._client.send_idle()

    def tick(self):
        if self._client.connected:
            force_update = time.time() - self._last_update > MainScreen.REFRESH_RATE
            if force_update and not self._screen_manager.is_screen_off():
                self._force_update()
            elif select([self._client], [], [], 0)[0]:
                self._idle_update_status()
        else:
            self._screen_manager.set_screen(self._status_screen)

    def on_keyboard_event(self, buttons_pressed):
        # print("on_kbd_event: noidle")
        self._stop_idle()
        resume_idle = True

        if buttons_pressed == [KeyboardManager.UP] or buttons_pressed == [KeyboardManager.DOWN]:
            self._screen_manager.set_screen(self._play_list_screen)
            resume_idle = False
        elif buttons_pressed == [KeyboardManager.LEFT]:
            volume = self._volmgr.volume
            volume = max(0, volume - 5)
            self._volmgr.set_volume(volume)
            self._volume.set_value(volume)
        elif buttons_pressed == [KeyboardManager.RIGHT]:
            volume = self._volmgr.volume
            volume = min(100, volume + 5)
            self._volmgr.set_volume(volume)
            self._volume.set_value(volume)
        elif buttons_pressed == [KeyboardManager.CENTER]:
            status = self._status.status
            if status == PlayingWidget.PLAYING:
                self._client.pause(1)
                self._status.set_status(PlayingWidget.PAUSED)
            elif status == PlayingWidget.PAUSED:
                self._client.pause(0)
                self._status.set_status(PlayingWidget.PLAYING)
        elif buttons_pressed == [KeyboardManager.A]:
            self._client.play_playlist(MainScreen.A_PLAYLIST)
        elif buttons_pressed == [KeyboardManager.B]:
            self._client.next()

        if resume_idle:
            # print("on_kbd_event: idle")
            self._client.send_idle()
