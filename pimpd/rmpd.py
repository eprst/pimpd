from mpd import MPDClient, ConnectionError
import threading
import socket


class ReconnectingClient(MPDClient):
    def __init__(self):
        super(ReconnectingClient, self).__init__(use_unicode=True)
        self.connectionStatus = "Initializing"
        self.lastConnectionFailure = None
        self.connected = False

        self._host = None
        self._port = None

        self._cond = threading.Condition()
        self._keepReconnecting = False
        self._reconnectThread = threading.Thread(target=self._reconnect)
        self._reconnectThread.setDaemon(True)
        self._reconnectThread.start()

    def disconnect(self):
        self._keepReconnecting = False
        if self.connected:
            self.connected = False
            super(ReconnectingClient, self).disconnect()

    def connect(self, host, port=None, timeout=None):
        if timeout:
            self.timeout = timeout

        self._cond.acquire()

        try:
            if self.connected:
                self.disconnect()

            self._host = host
            self._port = port
            self._keepReconnecting = True
            self._cond.notifyAll()

        finally:
            self._cond.release()

    def _connection_lost(self, reason):
        self._cond.acquire()

        try:
            self.lastConnectionFailure = reason
            if self.connected:
                self.connected = False
                super(ReconnectingClient, self).disconnect()
            self._cond.notifyAll()
        finally:
            self._cond.release()

    def _reconnect(self):
        self._cond.acquire()
        while True:
            if not self._keepReconnecting or self.connected:
                self._cond.wait()
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
