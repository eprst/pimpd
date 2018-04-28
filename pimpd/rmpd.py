from mpd import MPDClient, ConnectionError
from volmgr import VolumeManager
import threading
import socket


class ReconnectingClient(MPDClient, VolumeManager):
    def __init__(self):
        super(ReconnectingClient, self).__init__(use_unicode=True)
        self.connectionStatus = "Initializing"
        self.lastConnectionFailure = None
        self.connected = False

        self._host = None
        self._port = None

        self._threadResumeCond = threading.Condition()
        self._threadStartedCond = threading.Condition()

        self._keepReconnecting = False
        self._reconnectThread = threading.Thread(target=self._reconnect)
        self._reconnectThread.setDaemon(True)

        self._threadStartedCond.acquire()
        self._reconnectThread.start()
        self._threadStartedCond.wait()
        self._threadStartedCond.release()

    def disconnect(self):
        self._keepReconnecting = False
        if self.connected:
            self.connected = False
            super(ReconnectingClient, self).disconnect()

    def connect(self, host, port=None, timeout=None):
        if timeout:
            self.timeout = timeout

        self._threadResumeCond.acquire()

        try:
            if self.connected:
                self.disconnect()

            self._host = host
            self._port = port
            self._keepReconnecting = True
            self._threadResumeCond.notifyAll()

        finally:
            self._threadResumeCond.release()

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

    def _connection_lost(self, reason):
        self._threadResumeCond.acquire()

        try:
            self.lastConnectionFailure = reason
            if self.connected:
                self.connected = False
                super(ReconnectingClient, self).disconnect()
            self._threadResumeCond.notifyAll()
        finally:
            self._threadResumeCond.release()

    def _reconnect(self):
        self._threadResumeCond.acquire()

        # only needed the first time: notify constructor that
        # thread has started and acquired _threadResumeCond
        self._threadStartedCond.acquire()
        self._threadStartedCond.notifyAll()
        self._threadStartedCond.release()

        while True:
            if not self._keepReconnecting or self.connected:
                self._threadResumeCond.wait()
            else:  # Can there be spurious wake-ups in Python? Should we check again?
                self.connectionStatus = "Connecting to %s:%s" % (self._host, self._port)
                try:
                    super(ReconnectingClient, self).connect(self._host, self._port)
                    self.connected = True
                    self.connectionStatus = "Connected to %s:%s" % (self._host, self._port)
                except (socket.error, socket.timeout) as e:
                    self.lastConnectionFailure = self.connectionStatus = str(e)
                except Exception as e:
                    self.lastConnectionFailure = self.connectionStatus = str(e)
                    self._keepReconnecting = False  # fatal exception; stop

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
