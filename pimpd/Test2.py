import smgr
from contrast import ContrastScreen
from dimmer import Dimmer
from kbdmgr import KeyboardManager
from testscreen import WidgetsTestScreen
from mainscreen import MainScreen
from statusscreen import StatusScreen
import rmpd

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Refresh rate
REFRESH_RATE = 0.1

client = rmpd.ReconnectingClient()
client.timeout = 5
client.connect("192.168.1.155", 6600)

kmgr = KeyboardManager(ROTATE)
s = smgr.ScreenManager(ROTATE, REFRESH_RATE)

# dimmer = Dimmer(s, kmgr, 5, 10)
statusscreen = StatusScreen(s, kmgr, client)
#contrastscreen = ContrastScreen(s, kmgr, s.display)
#testscreen = WidgetsTestScreen(s, kmgr, contrastscreen)
main = MainScreen(s, kmgr, client, statusscreen)

s.set_screen(main)

s.run() # main loop

kmgr.stop()
if client.connected:
    client.disconnect()

