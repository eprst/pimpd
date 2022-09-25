import asyncio
import logging.handlers
import signal
import screenmanager
from dimmer import Dimmer
from keyboardmanager import KeyboardManager
from screens.main import MainScreen
from screens.status import StatusScreen
import reconnectingclient

# MPD connection settings
# MPD_HOST = '192.168.1.155'
MPD_HOST = 'localhost'
MPD_PORT = 6600
MPD_TIMEOUT = 5

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Dim screen after this seconds, or None
DIM_AFTER = 10
# Turn screen off after this seconds, or None. Turning screen off greatly reduces CPU usage
OFF_AFTER = 20

# Screen refresh rate in seconds
REFRESH_RATE = 0.1

# Use syslog for logging
USE_SYSLOG = True

# End of configuration #####################################################

# Logging
logging.getLogger().setLevel(logging.INFO)
if USE_SYSLOG:
    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_DAEMON)
    formatter = logging.Formatter('pimpd {%(pathname)s:%(lineno)d}: %(levelname)s %(message)s')
    syslog_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[syslog_handler])
    logging.getLogger().handlers = [syslog_handler]
else:
    logging.basicConfig(level=logging.INFO)


async def main():
    mpd_client = reconnectingclient.ReconnectingClient()
    mpd_client.timeout = MPD_TIMEOUT

    # may have other implementations in the future (snapcast, alsa)
    volume_manager = mpd_client

    screen_manager = screenmanager.ScreenManager(ROTATE, REFRESH_RATE)
    keyboard_manager = KeyboardManager(ROTATE)
    dimmer = None

    # dimmer must register it's keyboard callback first
    if DIM_AFTER is not None or OFF_AFTER is not None:
        dimmer = Dimmer(screen_manager, keyboard_manager, DIM_AFTER, OFF_AFTER,
                        # these buttons must be reported to the current screen even if they were used to wake screen up
                        # currently only <UP> is consumed, rest wake up the screen and are passed through
                        [KeyboardManager.RIGHT, KeyboardManager.DOWN, KeyboardManager.LEFT,
                         KeyboardManager.CENTER, KeyboardManager.A, KeyboardManager.B])

    mpd_client.connect(MPD_HOST, MPD_PORT)

    try:
        async def shutdown(sig, loop):
            from contextlib import suppress
            logging.info('Caught {0}'.format(sig.name))
            # tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
            # for task in tasks:
            #    task.print_stack()  # TODO remove
            mpd_client.close()
            keyboard_manager.stop()
            tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task
            loop.stop()

        loop = asyncio.get_event_loop()
        for signame in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(signame, lambda: asyncio.ensure_future(shutdown(signame, loop)))

        status_screen = StatusScreen(screen_manager, keyboard_manager, mpd_client)
        main_screen = MainScreen(screen_manager, keyboard_manager, mpd_client, status_screen, volume_manager, dimmer)
        await screen_manager.set_screen(main_screen)

        await screen_manager.run()
    finally:
        mpd_client.close()
        keyboard_manager.stop()

asyncio.run(main())
