import smgr
from contrast import ContrastScreen
from dimmer import Dimmer
from kbdmgr import KeyboardManager
from testscreen import WidgetsTestScreen
from mainscreen import MainScreen

# Rotate by 180? That's the way I have my PI positioned, bonnet joystick on the right
ROTATE = True

# Refresh rate
REFRESH_RATE = 0.1

kmgr = KeyboardManager(ROTATE)
s = smgr.ScreenManager(ROTATE, REFRESH_RATE)

dimmer = Dimmer(s, kmgr, 5, 10)
contrastscreen = ContrastScreen(s, kmgr, s.display)
testscreen = WidgetsTestScreen(s, kmgr, contrastscreen)
main = MainScreen(s, kmgr, None, None)

s.set_screen(main)

s.run() # main loop

kmgr.stop()

