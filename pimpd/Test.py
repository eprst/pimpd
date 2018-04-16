from __future__ import print_function
from __future__ import print_function

from mpd import ConnectionError

import rmpd
import time
import socket

client = rmpd.ReconnectingClient()
try:
    client.timeout = 5
    client.connect("192.168.1.155", 6600)
    while True:

        try:
            if client.connected:
                print("Status: %s" % client.status())
            else:
                print("Connection status: %s" % client.connectionStatus)
                print("Previous error: %s" % client.lastConnectionFailure)

            time.sleep(3)
        except (socket.timeout, ConnectionError) as e:
            print(e)

except KeyboardInterrupt:
    client.disconnect()
