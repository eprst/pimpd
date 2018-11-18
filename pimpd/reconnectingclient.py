from mpd import MPDClient, ConnectionError
from volumemanager import VolumeManager
import mpd
import threading
import socket
import logging
import traceback
import time


class ReconnectingClient(MPDClient, VolumeManager):
    reconnect_sleep_time = 1 # seconds

    def __init__(self):
        super(ReconnectingClient, self).__init__(use_unicode=True)
        self._set_status(u"Initializing")
        self.last_connection_failure = None
        self.connected = False

        self._host = None
        self._port = None

        self._connected_callbacks = []

        self._thread_resume_cond = threading.Condition()
        self._thread_started_cond = threading.Condition()

        self._keep_reconnecting = False
        # a flag which makes 'disconnect' keep current '_keep_reconnecting' value.
        # In general we would like 'disconnect' to set '_keep_reconnecting' to False
        # only when called by external code, but sometimes it's called by 'mpd/base.py',
        # i.e. our superclass. We want to treat such calls as '_disconnect' calls
        self._freeze_keep_reconnecting = False
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
        if not self._freeze_keep_reconnecting:
            self._keep_reconnecting = False
        self._disconnect()

    def _disconnect(self):
        # if self.connected:
        self.connected = False
        MPDClient.disconnect(self)

    def connect(self, host, port=None, timeout=None):
        if timeout:
            self.timeout = timeout

        self._thread_resume_cond.acquire()

        try:
            if self.connected:
                self._disconnect()

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
            return max(0,int(status['volume'])) # treat -1 as 0
        else:
            return 0

    def set_volume(self, volume):
        if self.connected:
            MPDClient.setvol(self, volume)

    def safe_noidle(self):
        if self.connected:
            try:
                MPDClient.noidle(self)
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
                try:
                    line = unicode(line)
                except UnicodeError:
                    pass # already unicode? give up..
        if not line.endswith("\n"):
            self._disconnect()
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

    def _set_status(self, status):
        self.connection_status = status
        logging.info("Connection status: %s" % status)

    def _connection_lost(self, reason):
        logging.warn("Connection lost: %s" % reason)
        self._thread_resume_cond.acquire()

        try:
            self.last_connection_failure = reason
            self._disconnect()
        except Exception as e: # shit happens inside mpd library sometimes
            logging.error(e.message)
            logging.error(traceback.format_exc())
        finally:
            self._thread_resume_cond.notifyAll()
            self._thread_resume_cond.release()

    def _connected(self):
        self._set_status(u"Connected to %s:%s" % (self._host, self._port))
        for callback in self._connected_callbacks:
            callback()
        self.connected = True

    def _reconnect(self):
        self._thread_resume_cond.acquire()

        # only needed the first time: notify constructor that
        # thread has started and acquired _threadResumeCond
        self._thread_started_cond.acquire()
        self._thread_started_cond.notifyAll()
        self._thread_started_cond.release()

        while True:
            if self.connected or not self._keep_reconnecting:
                logging.info("Waiting")
                self._thread_resume_cond.wait()
            else:  # Can there be spurious wake-ups in Python? Should we check again?
                self._set_status(u"Connecting to %s:%s" % (self._host, self._port))
                try:
                    try:
                        self._freeze_keep_reconnecting = True
                        MPDClient.connect(self, self._host, self._port)
                    finally:
                        self._freeze_keep_reconnecting = False
                    self._connected()
                except (socket.error, socket.timeout) as e:
                    self.connected = False
                    self.last_connection_failure = u"Non-fatal: %s" % unicode(e)
                    self._set_status(self.last_connection_failure)
                    logging.info("Sleeping before retrying")
                    time.sleep(ReconnectingClient.reconnect_sleep_time)
                    logging.info("Retrying")
                except Exception as e:
                    self.connected = False
                    self.last_connection_failure = u"Fatal: %s" % unicode(e)
                    self._set_status(self.last_connection_failure)
                    # self._keep_reconnecting = False  # fatal exception; stop
                    raise

    def __getattribute__(self, item):
        attr = MPDClient.__getattribute__(self, item)
        if hasattr(attr, '__call__'):
            def wrapper(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except (socket.timeout, ConnectionError, mpd.base.CommandError) as err:
                    self._connection_lost(str(err))
                    raise
                except mpd.base.PendingCommandError:
                    logging.info('Pending commands: {}'.format(self._pending))
                    raise

            return wrapper
        else:
            return attr
