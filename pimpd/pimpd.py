import screenmanager
from dimmer import Dimmer
from kbdmgr import KeyboardManager
from screens.main import MainScreen
from screens.status import StatusScreen
import reconnectingclient


# MPD connection settings
MPD_HOST = '192.168.1.155'
MPD_PORT = 6600
MPD_TIMEOUT = 5

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Dim screen after this seconds, or None
DIM_AFTER = 20
# Turn screen off after this seconds, or None. Turning screen off greately reduces CPU usage
OFF_AFTER = 30

# Screen refresh rate in seconds
REFRESH_RATE = 0.1

########################################################

mpd_client = reconnectingclient.ReconnectingClient()
mpd_client.timeout = MPD_TIMEOUT
mpd_client.connect(MPD_HOST, MPD_PORT)

# may have other implementations in the future (snapcast, alsa)
volume_manager = mpd_client

keyboard_manager = KeyboardManager(ROTATE)
screen_manager = screenmanager.ScreenManager(ROTATE, REFRESH_RATE)

if DIM_AFTER is not None or OFF_AFTER is not None:
    Dimmer(screen_manager, keyboard_manager, DIM_AFTER, OFF_AFTER)

status_screen = StatusScreen(screen_manager, keyboard_manager, mpd_client)
main = MainScreen(screen_manager, keyboard_manager, mpd_client, status_screen, volume_manager)

screen_manager.set_screen(main)

screen_manager.run() # main loop

keyboard_manager.stop()
if mpd_client.connected:
    mpd_client.disconnect()

