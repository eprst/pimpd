from __future__ import print_function
from __future__ import print_function

from mpd import ConnectionError
from select import select

import rmpd
import time
import socket

client = rmpd.ReconnectingClient()


def connected():
    print("Connected!")
    client.send_idle()
    update()

def update():
    print("update()")
    print(client.currentsong())
    print(client.status())
    print("/update()")

try:
    client.timeout = 5
    client.connect("192.168.1.155", 6600)
    client.add_connected_callback(connected)

    while True:

        try:
            if client.connected:
                can_read = select([client], [], [], 0)[0]
                if can_read:
                    changes = client.fetch_idle()
                    print(changes) # handle changes
                    update()
                    client.send_idle() # continue idling

                # print("Volume: %d" % client.volume)
            else:
                print("Connection status: %s" % client.connection_status)
                print("Previous error: %s" % client.last_connection_failure)

            time.sleep(3)
        except (socket.timeout, ConnectionError) as e:
            print(e)

except KeyboardInterrupt:
    client.disconnect()
