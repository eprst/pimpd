import asyncio
import logging
import socket
import traceback

import mpd
from mpd.asyncio import MPDClient
import tasklogger

from volumemanager import VolumeManager


class ReconnectingClient(MPDClient, VolumeManager):
    reconnect_sleep_time = 1  # seconds

    def __init__(self):
        super(ReconnectingClient, self).__init__()
        self._set_status(u"Initializing")
        self.last_connection_failure = None
        self._connected = False

        self._host = None
        self._port = None

        self._connected_callbacks = []
        self._idle_callbacks = []
        self._keep_reconnecting = False
        # special handling for Exceptions happening inside mpd/asyncio
        # which then calls disconnect(). We don't want to stop reconnecting
        # in such cases
        self._disconnect_not_caused_by_us = False

        self._disconnected_event = asyncio.Event()
        self._reconnect_task = tasklogger.create_task(self._reconnect_loop())
        self._reconnect_task.add_done_callback(self._handle_reconnect_result)

        self._last_volume = 0

        self._idle_task: asyncio.Task | None = None

    @staticmethod
    def _handle_reconnect_result(task: asyncio.Task) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.info(e)
        except KeyboardInterrupt as e:
            logging.info(e)

    async def add_connected_callback(self, callback):
        self._connected_callbacks.append(callback)
        if self._connected:
            await callback()

    def remove_connected_callback(self, callback):
        self._connected_callbacks.remove(callback)

    def add_idle_callback(self, callback):
        self._idle_callbacks.append(callback)

    def remove_idle_callback(self, callback):
        try:
            self._idle_callbacks.remove(callback)
        except ValueError:
            pass

    def disconnect(self):
        if self._disconnect_not_caused_by_us:
            self._disconnect_not_caused_by_us = False
        else:
            self._keep_reconnecting = False
        self._disconnect()

    def close(self):
        if self._connected:
            self.disconnect()
        self._reconnect_task.cancel()

    def _disconnect(self):
        self._on_disconnected()
        try:
            MPDClient.disconnect(self)
        finally:
            self._disconnected_event.set()

    def connect(self, host, port=6600, loop=None):
        self._host = host
        self._port = port
        self._keep_reconnecting = True

        if self._connected:
            self._disconnect()
        else:
            self._disconnected_event.set()

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    async def volume(self) -> int:
        if self._connected:
            try:
                status = await asyncio.wait_for(MPDClient.status(self), timeout=1)
                self._last_volume = max(0, int(status['volume']))  # treat -1 as 0
                return self._last_volume
            except asyncio.TimeoutError:
                # pympd bug workaround
                return self._last_volume
            except mpd.base.ProtocolError:
                # pympd glitch
                self._disconnect_not_caused_by_us = True
                raise
        else:
            return 0

    async def set_volume(self, volume: int) -> None:
        if self._connected:
            try:
                await asyncio.wait_for(MPDClient.setvol(self, volume), timeout=1)
            except asyncio.TimeoutError:
                # pympd bug workaround
                return 0
            except mpd.base.ProtocolError:
                # pympd glitch
                self._disconnect_not_caused_by_us = True
                self._disconnect()

    async def play_playlist(self, name: str) -> None:
        await self.clear()
        await self.load(name)
        await self.play(0)

    def _set_status(self, status):
        self.connection_status = status
        logging.info(f"Connection status: {status}")

    def _connection_lost(self, reason):
        logging.warning(f"Connection lost: {reason}")

        try:
            self.last_connection_failure = reason
            self._disconnect()
            self._keep_reconnecting = True
        except Exception as e:  # shit happens inside mpd library sometimes
            logging.error(e)
            logging.error(traceback.format_exc())

    async def _on_connected(self):
        self._set_status(f"Connected to {self._host}:{self._port}")
        self._connected = True
        for callback in self._connected_callbacks:
            await callback()
        self._disconnected_event.clear()
        self._idle_task = tasklogger.create_task(self._idle_loop())

    def _on_disconnected(self):
        self._connected = False
        if self._idle_task is not None:
            self._idle_task.cancel()
            self._idle_task = None

    async def _idle_loop(self):
        try:
            async for s in self.idle():
                for callback in self._idle_callbacks:
                    await callback(s)
        except asyncio.CancelledError:
            pass

    async def _reconnect_loop(self):
        while True:

            if self._connected or not self._keep_reconnecting:
                logging.info('Waiting')
                await self._disconnected_event.wait()
                self._disconnected_event.clear()
                # await asyncio.sleep(ReconnectingClient.reconnect_sleep_time)
            else:  # Can there be spurious wake-ups in Python? Should we check again?
                self._set_status(f"Connecting to {self._host}:{self._port}")
                try:
                    await MPDClient.connect(self, self._host, self._port)
                    await self._on_connected()
                except (socket.error, socket.timeout, mpd.ConnectionError) as e:
                        # I don't like catching cancelled and timeout errors,
                        # but that's what mpd/asyncio is throwing sometimes
                        # asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError) as e:
                    self.last_connection_failure = u"Non-fatal: %s" % str(e)
                    self._set_status(self.last_connection_failure)
                    self._on_disconnected()
                    self._disconnected_event.set()
                    logging.info("Sleeping before retrying")
                    await asyncio.sleep(ReconnectingClient.reconnect_sleep_time)
                    logging.info("Retrying")
                except Exception as e:
                    logging.exception("connection failure")
                    self.last_connection_failure = u"Fatal: %s" % str(e)
                    self._set_status(self.last_connection_failure)
                    self._on_disconnected()
                    # self._keep_reconnecting = False  # fatal exception; stop
                    raise

    def __getattribute__(self, item):
        attr = MPDClient.__getattribute__(self, item)
        if hasattr(attr, '__call__'):
            def wrapper(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                    # print("in {}".format(attr))
                    # res = attr(*args, **kwargs)
                    # print("out {}".format(attr))
                    # return res
                # except (socket.timeout, mpd.base.ConnectionError, mpd.base.Comm) as err:
                #     print("BOOOOM0")
                #     self._connection_lost(str(err))
                #     raise
                # except mpd.base.PendingCommandError:
                #     logging.info('Pending commands: {}'.format(self._pending))
                #     raise
                except mpd.base.ConnectionError as e:
                    self._connection_lost(str(e))
                    raise
                except mpd.base.ProtocolError:
                    # pympd glitch
                    self._disconnect_not_caused_by_us = True
                    raise


            return wrapper
        else:
            return attr

    def command_list_ok_begin(self):
        pass

    def command_list_end(self):
        pass
