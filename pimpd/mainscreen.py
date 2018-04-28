from screen import Screen
from stext import ScrollingText
from rpmd import ReconnectingClient
from PIL import ImageFont


class MainScreen(Screen):
    def __init__(self, screen_manager, keyboard_manager, client, statusscreen):
        super(StatusScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        self._statusscreen = statusscreen
        font = ImageFont.truetype("DejaVuSans.ttf", 12)

    def widgets(self):
        return []
