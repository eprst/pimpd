# from __future__ import print_function

import asyncio
import logging

# import reconnectingclient
from mpd.asyncio import MPDClient

client = None


async def connected():
    print("Connected!")
    asyncio.create_task(idle_loop())
    while True:
        try:
           await asyncio.sleep(0.1)
           st = await client.status()
           volume = max(0, int(st.get('volume', 0)))
           await client.setvol(volume+1)
           await asyncio.sleep(0.09)
           await client.status()
           await asyncio.sleep(0.01)
           await client.status()
           await asyncio.sleep(0.01)
           await client.setvol(volume)
           await asyncio.sleep(0.09)
           await client.status()
        except Exception as e:
            print(e)
    # await update()
    # while client.connected:
    #     print("tick")
    #     try:
    #         async for subsystem in client.idle():
    #             print("Idle change in %s" % subsystem)
    #             await update()
    #     except mpd.base.ConnectionError:
    #         print("Connection lost, I'm done")


async def idle_loop():
    async for s in client.idle():
        await idle(s)

async def idle(subsystems: list[str]) -> None:
    print("Idle change in", subsystems)
    # await update()


async def update():
    print("update()")
    # cs = await client.currentsong()
    # print('artist: {}'.format(cs.get('artist', '???')))
    # print('title: {}'.format(cs.get('title', None)))
    # print('file: {}'.format(cs.get('file', None)))

    st = await client.status()
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
    print([t['playlist'] async for t in lists])
    print("/update()")


async def main():
    global client
    client = MPDClient()
    #client = reconnectingclient.ReconnectingClient()

    try:
        client.timeout = 5
        # client.connect("192.168.1.155", 6600)
        await client.connect("127.0.0.1", 6600)
        await connected()
        # await client.add_connected_callback(connected)
        # client.add_idle_callback(idle)

        # await asyncio.Event().wait()  # sleep forever

        # while True:
        #     print("tick")
        #     try:
        #         if client.connected:
        #             async for subsystem in client.idle():
        #                 print("Idle change in %s" % subsystem)
        #                 await update()
        #             # await update()
        #         else:
        #             print("Connection status: %s" % client.connection_status)
        #             print("Previous error: %s" % client.last_connection_failure)
        #
        #         await asyncio.sleep(1)
        #     except mpd.base.ConnectionError:
        #         print("Connection lost")

    except KeyboardInterrupt:
        print("<><>><><><><><<")
        client.close()


# def shutdown(sig, frame):
#     print("sh<<")
#     client.close()
#     asyncio.get_event_loop().close()
#     asyncio.get_event_loop().stop()
#
#
# for signame in (signal.SIGINT, signal.SIGTERM):
#     signal.signal(signame, shutdown)

log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Bye")
