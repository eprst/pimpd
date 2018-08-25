# -*- coding: utf-8 -*-
import time
from select import select
import socket

import mpd
import fonts

from widgets.progressbar import ProgressBar
from widgets.playing import PlayingWidget
from screen import Screen
from widgets.scrollingtext import ScrollingText
from keyboardmanager import KeyboardManager
from screens.playlists import PlayListsScreen


class MainScreen(Screen):
    # refresh on updates from server or every <REFRESH_RATE> seconds
    REFRESH_RATE = 5
    # playlist to start on pressing 'A' button
    A_PLAYLIST = u'Дождь'
    # playlist to start on pressing 'A' and 'B' buttons together
    # (doesn't work, have to debug)
    AB_PLAYLIST = u'шум со звуком в конце'
    # volume adjustment step
    VOLUME_STEP = 3

    def __init__(self, screen_manager, keyboard_manager, client, status_screen, volmgr):
        super(MainScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        self._status_screen = status_screen
        self._volmgr = volmgr

        font = fonts.DEFAULT_FONT_14

        self._status = PlayingWidget((0, 0), (9, 9))
        self._seekbar = ProgressBar((24, 1), (128 - 24, 7), 100)

        self._artist = ScrollingText((0, 12), (128, 16), font, u'')

        self._title = ScrollingText((0, 32), (128, 16), font, u'')

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
            self._artist.set_text(u'<stopped>')
            self._title.set_text(u'')
        elif isinstance(cs, basestring):
            # got this once, not sure what it means
            self._artist.set_text(cs)
            self._title.set_text(cs)
        else:
            artist = cs.get('artist')
            name = cs.get('name')
            if artist is not None:
                self._artist.set_text(artist)
            elif name is not None:
                self._artist.set_text(name)
            else:
                self._artist.set_text(u'Unknown Artist')

            title = cs.get('title', None)
            file = cs.get('file', None)
            if title is not None:
                self._title.set_text(title)
            elif file is not None:
                self._title.set_text(file)
            else:
                self._title.set_text(u'Unknown Title')

        elapsed = float(st.get('elapsed', 0.0))
        duration = float(st.get('duration', 0.0))
        if elapsed == 0 or duration == 0:
            _time = st.get('time', '0:0').split(':')
            elapsed = float(_time[0])
            duration = float(_time[1])
        if duration > 0:
            self._seekbar.set_value(elapsed * 100 / duration)
        else:
            self._seekbar.set_value(0)

        volume = self._volmgr.volume
        self._volume.set_value(volume)

        self._last_update = time.time()

    def _stop_idle(self):
        self._client.safe_noidle()

    def _force_update(self):
        # print("_force_update: noidle")
        self._stop_idle()
        self._update_status()
        # print("_force_update: idle")
        self._client.send_idle()

    def tick(self):
        try:
            if self._client.connected:
                force_update = time.time() - self._last_update > MainScreen.REFRESH_RATE
                if force_update and not self._screen_manager.is_screen_off():
                    self._force_update()
                elif select([self._client], [], [], 0)[0]:
                    self._idle_update_status()
            else:
                self._screen_manager.set_screen(self._status_screen)
        except (socket.timeout, mpd.ConnectionError):
            self._screen_manager.set_screen(self._status_screen)

    def on_keyboard_event(self, buttons_pressed):
        # print("on_kbd_event: noidle")
        self._stop_idle()
        try:

            resume_idle = True

            if buttons_pressed == [KeyboardManager.UP] or buttons_pressed == [KeyboardManager.DOWN]:
                self._screen_manager.set_screen(self._play_list_screen)
                resume_idle = False
            elif buttons_pressed == [KeyboardManager.LEFT]:
                volume = self._volmgr.volume
                volume = max(0, volume - MainScreen.VOLUME_STEP)
                self._volmgr.set_volume(volume)
                self._volume.set_value(volume)
            elif buttons_pressed == [KeyboardManager.RIGHT]:
                volume = self._volmgr.volume
                volume = min(100, volume + MainScreen.VOLUME_STEP)
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
            elif buttons_pressed == [KeyboardManager.A, KeyboardManager.B]:
                self._client.play_playlist(MainScreen.AB_PLAYLIST)
            elif buttons_pressed == [KeyboardManager.B]:
                status = self._status.status
                if status == PlayingWidget.PLAYING:
                    self._client.next()

            if resume_idle:
                # print("on_kbd_event: idle")
                self._client.send_idle()

        except (socket.timeout, mpd.ConnectionError):
            self._screen_manager.set_screen(self._status_screen)
