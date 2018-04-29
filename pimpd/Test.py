from __future__ import print_function
from __future__ import print_function

from select import select

import mpd
import reconnectingclient
import time
import socket

client = reconnectingclient.ReconnectingClient()


def connected():
    print("Connected!")
    update()
    client.send_idle()


def update():
    print("update()")
    cs = client.currentsong()
    print('artist: {}'.format(cs.get('artist', '???')))
    print('title: {}'.format(cs.get('title', None)))
    print('file: {}'.format(cs.get('file', None)))

    st = client.status()
    elapsed = float(st.get('elapsed', 0.0))
    if elapsed == 0.0:
        elapsed = float(st.get('time', 0.0))
    state = st.get('state', 'stop')  # play/stop/pause
    volume = int(st.get('volume', 0))
    duration = float(st.get('duration', 0.0))

    if duration > 0:
        print('state: {}, volume: {}, position: {}%'.format(state, volume, elapsed * 100 / duration))
    else:
        print('state: {}, volume: {}'.format(state, volume))

    print(st)

    lists = client.listplaylists()
    print([t['playlist'] for t in lists])
    print("/update()")


def idle_update():
    try:
        client.fetch_idle()
    except mpd.base.PendingCommandError:
        pass

    update()
    client.send_idle()  # continue idling


try:
    client.timeout = 5
    client.connect("192.168.1.155", 6600)
    client.add_connected_callback(connected)

    while True:

        try:
            if client.connected:
                can_read = select([client], [], [], 0)[0]
                if can_read:
                    idle_update()

                # print("Volume: %d" % client.volume)
            else:
                print("Connection status: %s" % client.connection_status)
                print("Previous error: %s" % client.last_connection_failure)

            time.sleep(3)
        except (socket.timeout, mpd.ConnectionError) as e:
            print(e)

except KeyboardInterrupt:
    client.disconnect()
