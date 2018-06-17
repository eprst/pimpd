from mpd import MPDClient, ConnectionError
from volumemanager import VolumeManager
import mpd
import threading
import socket
import logging
import traceback


class ReconnectingClient(MPDClient, VolumeManager):
    def __init__(self):
        super(ReconnectingClient, self).__init__(use_unicode=True)
        self.connection_status = u"Initializing"
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
            MPDClient.disconnect(self)

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

    def safe_noidle(self):
        if self.connected:
            try:
                self.noidle()
            except mpd.base.CommandError:
                pass

    def play_playlist(self, name):
        self.safe_noidle()
        self.clear()
        self.load(name)
        self.play(0)

    def currentsong(self):
        try:
            return MPDClient.currentsong(self)
        except UnicodeDecodeError as e:
            return str(e)

    # override _read_line to be more tolerant to unicode errors
    def _read_line(self):
        line = self._rfile.readline()
        if self.use_unicode:
            try:
                # why isn't it an overloadable method?
                line = unicode(line, "utf-8")
            except UnicodeError:
                line = unicode(line)
        if not line.endswith("\n"):
            self.disconnect()
            raise ConnectionError("Connection lost while reading line")
        line = line.rstrip("\n")
        if line.startswith(mpd.base.ERROR_PREFIX):
            error = line[len(mpd.base.ERROR_PREFIX):].strip()
            raise mpd.base.CommandError(error)
        if self._command_list is not None:
            if line == mpd.base.NEXT:
                return
            if line == mpd.base.SUCCESS:
                raise mpd.base.ProtocolError("Got unexpected '{}'".format(mpd.base.SUCCESS))
        elif line == mpd.base.SUCCESS:
            return
        return line

    def _connection_lost(self, reason):
        self._thread_resume_cond.acquire()

        try:
            self.last_connection_failure = reason
            if self.connected:
                self.connected = False
                MPDClient.disconnect(self)
        except Exception as e: # shit happens inside mpd library sometimes
            logging.error(e.message)
            logging.error(traceback.format_exc())
        finally:
            self._thread_resume_cond.notifyAll()
            self._thread_resume_cond.release()

    def _connected(self):
        self.connected = True
        self.connection_status = u"Connected to %s:%s" % (self._host, self._port)
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
                self.connection_status = u"Connecting to %s:%s" % (self._host, self._port)
                try:
                    MPDClient.connect(self, self._host, self._port)
                    self._connected()
                except (socket.error, socket.timeout) as e:
                    self.last_connection_failure = self.connection_status = unicode(e)
                except Exception as e:
                    self.last_connection_failure = self.connection_status = unicode(e)
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
                    raise
                except mpd.base.PendingCommandError:
                    logging.info('Pending commands: {}'.format(self._pending))
                    raise

            return wrapper
        else:
            return attr
