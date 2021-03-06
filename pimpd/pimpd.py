import logging
import logging.handlers
import signal
import screenmanager
from dimmer import Dimmer
from keyboardmanager import KeyboardManager
from screens.main import MainScreen
from screens.status import StatusScreen
import reconnectingclient

# MPD connection settings
#MPD_HOST = '192.168.1.155'
MPD_HOST = 'localhost'
MPD_PORT = 6600
MPD_TIMEOUT = 5

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Dim screen after this seconds, or None
DIM_AFTER = 20
# Turn screen off after this seconds, or None. Turning screen off greatly reduces CPU usage
OFF_AFTER = 30

# Screen refresh rate in seconds
REFRESH_RATE = 0.1

# End of configuration #####################################################

# Logging 
syslog_handler=logging.handlers.SysLogHandler(address='/dev/log', facility=logging.handlers.SysLogHandler.LOG_DAEMON)
formatter = logging.Formatter('pimpd {%(pathname)s:%(lineno)d}: %(levelname)s %(message)s')
syslog_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[syslog_handler])
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().handlers = [ syslog_handler ]

mpd_client = reconnectingclient.ReconnectingClient()
mpd_client.timeout = MPD_TIMEOUT
mpd_client.connect(MPD_HOST, MPD_PORT)

# may have other implementations in the future (snapcast, alsa)
volume_manager = mpd_client

keyboard_manager = KeyboardManager(ROTATE)
screen_manager = screenmanager.ScreenManager(ROTATE, REFRESH_RATE)

def on_kill(signum, frame):
    screen_manager.shutdown()

signal.signal(signal.SIGTERM, on_kill)
signal.signal(signal.SIGINT, on_kill)

if DIM_AFTER is not None or OFF_AFTER is not None:
    Dimmer(screen_manager, keyboard_manager, DIM_AFTER, OFF_AFTER,
           # these buttons must be reported to the current screen even if they were used to wake screen up
           # currently only <UP> is consumed, rest wake up the screen and are passed through
           [KeyboardManager.RIGHT, KeyboardManager.DOWN, KeyboardManager.LEFT,
            KeyboardManager.CENTER, KeyboardManager.A, KeyboardManager.B])

status_screen = StatusScreen(screen_manager, keyboard_manager, mpd_client)
main = MainScreen(screen_manager, keyboard_manager, mpd_client, status_screen, volume_manager)

screen_manager.set_screen(main)

screen_manager.run()  # main loop

keyboard_manager.stop()
if mpd_client.connected:
    mpd_client.disconnect()
