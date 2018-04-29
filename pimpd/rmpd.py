from mpd import MPDClient, ConnectionError
from volmgr import VolumeManager
import threading
import socket


class ReconnectingClient(MPDClient, VolumeManager):
    def __init__(self):
        super(ReconnectingClient, self).__init__(use_unicode=True)
        self.connection_status = "Initializing"
        self.last_connection_failure = None
        self.connected = False

        self._host = None
        self._port = None

        self._connected_callbacks = []

        self._thread_resume_cond = threading.Condition()
        self._thread_started_cond = threading.Condition()

        self._keep_reconnecting = False
        self._reconnect_thread = threading.Thread(target=self._reconnect)
        self._reconnect_thread.setDaemon(True)

        self._thread_started_cond.acquire()
        self._reconnect_thread.start()
        self._thread_started_cond.wait()
        self._thread_started_cond.release()

    def add_connected_callback(self, callback):
        self._connected_callbacks.append(callback)
        if self.connected:
            callback()

    def remove_connected_callback(self, callback):
        self._connected_callbacks.remove(callback)

    def disconnect(self):
        self._keep_reconnecting = False
        if self.connected:
            self.connected = False
            super(ReconnectingClient, self).disconnect()

    def connect(self, host, port=None, timeout=None):
        if timeout:
            self.timeout = timeout

        self._thread_resume_cond.acquire()

        try:
            if self.connected:
                self.disconnect()

            self._host = host
            self._port = port
            self._keep_reconnecting = True
            self._thread_resume_cond.notifyAll()

        finally:
            self._thread_resume_cond.release()

    @property
    def volume(self):
        if self.connected:
            status = MPDClient.status(self)
            return int(status['volume'])
        else:
            return 0

    def set_volume(self, volume):
        if self.connected:
            MPDClient.setvol(self, volume)

    def currentsong(self):
        try:
            return MPDClient.currentsong(self)
        except UnicodeDecodeError as e:
            return str(e)

    def _connection_lost(self, reason):
        self._thread_resume_cond.acquire()

        try:
            self.last_connection_failure = reason
            if self.connected:
                self.connected = False
                super(ReconnectingClient, self).disconnect()
            self._thread_resume_cond.notifyAll()
        finally:
            self._thread_resume_cond.release()

    def _connected(self):
        self.connected = True
        self.connection_status = "Connected to %s:%s" % (self._host, self._port)
        for callback in self._connected_callbacks:
            callback()

    def _reconnect(self):
        self._thread_resume_cond.acquire()

        # only needed the first time: notify constructor that
        # thread has started and acquired _threadResumeCond
        self._thread_started_cond.acquire()
        self._thread_started_cond.notifyAll()
        self._thread_started_cond.release()

        while True:
            if not self._keep_reconnecting or self.connected:
                self._thread_resume_cond.wait()
            else:  # Can there be spurious wake-ups in Python? Should we check again?
                self.connection_status = "Connecting to %s:%s" % (self._host, self._port)
                try:
                    super(ReconnectingClient, self).connect(self._host, self._port)
                    self._connected()
                except (socket.error, socket.timeout) as e:
                    self.last_connection_failure = self.connection_status = str(e)
                except Exception as e:
                    self.last_connection_failure = self.connection_status = str(e)
                    self._keep_reconnecting = False  # fatal exception; stop
                    raise

    def __getattribute__(self, item):
        attr = MPDClient.__getattribute__(self, item)
        if hasattr(attr, '__call__'):
            def wrapper(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except (socket.timeout, ConnectionError) as err:
                    self._connection_lost(str(err))
                    raise err

            return wrapper
        else:
            return attr
