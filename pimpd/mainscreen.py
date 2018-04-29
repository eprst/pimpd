from screen import Screen
from stext import ScrollingText
from statusscreen import StatusScreen
from rmpd import ReconnectingClient
from playing import PlayingWidget
from pbar import ProgressBar

from PIL import ImageFont


class MainScreen(Screen):
    def __init__(self, screen_manager, keyboard_manager, client, status_screen):
        super(MainScreen, self).__init__(screen_manager, keyboard_manager)
        self._client = client
        self._status_screen = status_screen
        font = ImageFont.truetype("DejaVuSans.ttf", 12)

        self._status = PlayingWidget((0, 0), (9, 9))
        self._seekbar = ProgressBar((14, 1), (128 - 14, 7), 100)
        self._artist = ScrollingText((0, 10), (128, 12), font, '')
        self._title = ScrollingText((0, 25), (128, 12), font, '')
        self._volume_label = ScrollingText((0, 40), (40, 12), font, 'Volume')
        self._volume = ProgressBar((42, 40), (128 - 42, 10), 100)

        # temp. testing
        self._status.set_status(PlayingWidget.PLAYING)
        self._seekbar.set_value(50)
        self._artist.set_text('Artist')
        self._title.set_text('Title')
        self._volume.set_value(50)

    def widgets(self):
        return [self._status, self._seekbar, self._artist, self._title,
                self._volume_label, self._volume]
