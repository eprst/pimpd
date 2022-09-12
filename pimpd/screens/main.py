# -*- coding: utf-8 -*-
import socket

import mpd
import fonts
import logging
import asyncio

import keyboardmanager
import reconnectingclient
import screenmanager
import screens.status
import volumemanager
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
    AB_PLAYLIST = u'Спи, моя радость, усни'
    # volume adjustment step
    VOLUME_STEP = 3

    def __init__(self,
                 screen_manager: screenmanager.ScreenManager,
                 keyboard_manager: keyboardmanager.KeyboardManager,
                 client: reconnectingclient.ReconnectingClient,
                 status_screen: screens.status.StatusScreen,
                 volmgr: volumemanager.VolumeManager):
        super(MainScreen, self).__init__(screen_manager, keyboard_manager)
        font = fonts.DEFAULT_FONT_14

        self._client = client
        self._status_screen = status_screen
        self._volmgr = volmgr

        self._status = PlayingWidget((0, 0), (9, 9))
        self._seekbar = ProgressBar((24, 1), (128 - 24, 7), 100)
        self._artist = ScrollingText((0, 12), (128, 16), font, u'')
        self._title = ScrollingText((0, 32), (128, 16), font, u'')
        self._volume = ProgressBar((0, 54), (128, 7), 100)
        self._play_list_screen = PlayListsScreen(screen_manager, keyboard_manager, client)

    def widgets(self):
        return [self._status, self._seekbar, self._artist, self._title,
                # self._volume_label, self._volume]
                self._volume]

    async def activate(self):
        await super(MainScreen, self).activate()
        # this will immediately trigger _connected if already connected
        await self._client.add_connected_callback(self._connected)
        self._client.add_idle_callback(self._idle)

    def deactivate(self):
        super(MainScreen, self).deactivate()
        self._client.remove_connected_callback(self._connected)
        self._client.remove_idle_callback(self._idle)

    async def _connected(self):
        logging.info("Main screen connected, forcing update")
        await self._update_status()

    async def _idle(self, subsystems: list[str]) -> None:
        await self._update_status()

    async def _update_status(self):
        if self._client.connected:
            if not self._screen_manager.is_screen_off():
                await self._update_status_connected()
        else:
            await self._screen_manager.set_screen(self._status_screen)

    async def _update_status_connected(self):
        st = await self._client.status()
        cs = await self._client.currentsong()

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

        volume = await self._volmgr.volume
        self._volume.set_value(volume)

    async def on_keyboard_event(self, buttons_pressed: list[int]) -> bool:
        try:
            if buttons_pressed == [KeyboardManager.UP] or buttons_pressed == [KeyboardManager.DOWN]:
                await self._screen_manager.set_screen(self._play_list_screen)
            elif buttons_pressed == [KeyboardManager.LEFT]:
                volume = await self._volmgr.volume
                # await asyncio.sleep(0.09)  # magic to avoid pympd race
                volume = max(0, volume - MainScreen.VOLUME_STEP)
                await self._volmgr.set_volume(volume)
                self._volume.set_value(volume)
            elif buttons_pressed == [KeyboardManager.RIGHT]:
                volume = await self._volmgr.volume
                # await asyncio.sleep(0.09)  # magic to avoid pympd race
                volume = min(100, volume + MainScreen.VOLUME_STEP)
                await self._volmgr.set_volume(volume)
                self._volume.set_value(volume)
            elif buttons_pressed == [KeyboardManager.CENTER]:
                status = self._status.status
                if status == PlayingWidget.PLAYING:
                    await self._client.pause(1)
                    self._status.set_status(PlayingWidget.PAUSED)
                elif status == PlayingWidget.PAUSED:
                    await self._client.pause(0)
                    self._status.set_status(PlayingWidget.PLAYING)
            elif buttons_pressed == [KeyboardManager.A]:
                await self._client.play_playlist(MainScreen.A_PLAYLIST)
            elif buttons_pressed == [KeyboardManager.A, KeyboardManager.B]:
                await self._client.play_playlist(MainScreen.AB_PLAYLIST)
            elif buttons_pressed == [KeyboardManager.B]:
                status = self._status.status
                if status == PlayingWidget.PLAYING:
                    await self._client.next()
            else:
                return False

            return True

        except (socket.timeout, mpd.ConnectionError):
            await self._screen_manager.set_screen(self._status_screen)
            return False
