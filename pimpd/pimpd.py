import smgr
from contrast import ContrastScreen
from dimmer import Dimmer
from kbdmgr import KeyboardManager
from testscreen import WidgetsTestScreen
from mainscreen import MainScreen
from statusscreen import StatusScreen
import rmpd


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

client = rmpd.ReconnectingClient()
client.timeout = MPD_TIMEOUT
client.connect(MPD_HOST, MPD_PORT)

kmgr = KeyboardManager(ROTATE)
s = smgr.ScreenManager(ROTATE, REFRESH_RATE)

if DIM_AFTER is not None or OFF_AFTER is not None:
    Dimmer(s, kmgr, DIM_AFTER, OFF_AFTER)

statusscreen = StatusScreen(s, kmgr, client)
main = MainScreen(s, kmgr, client, statusscreen, client)

s.set_screen(main)

s.run() # main loop

kmgr.stop()
if client.connected:
    client.disconnect()

