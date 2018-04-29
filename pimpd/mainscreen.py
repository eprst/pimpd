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
        font = ImageFont.truetype("DejaVuSans.ttf", 14)

        self._status = PlayingWidget((0, 0), (9, 9))
        self._seekbar = ProgressBar((14, 1), (128 - 14, 7), 100)

        self._artist = ScrollingText((0, 12), (128, 15), font, '')

        self._title = ScrollingText((0, 32), (128, 15), font, '')

        #self._volume_label = ScrollingText((-2, 50), (50, 13), font, ' Volume')
        # self._volume_label.set_draw_border(True)
        #self._volume = ProgressBar((55, 54), (128 - 55, 7), 100)
        
        self._volume = ProgressBar((0, 54), (128, 7), 100)

        # temp. testing
        self._status.set_status(PlayingWidget.PLAYING)
        self._seekbar.set_value(100)
        self._artist.set_text('Artist aaaaaaaa')
        self._title.set_text('Title aaaaaaaaa')
        self._volume.set_value(100)

    def widgets(self):
        return [self._status, self._seekbar, self._artist, self._title,
                # self._volume_label, self._volume]
                self._volume]
    
    def _update_status(self):
        try:
            status = self._client.status()
            self._artist.set_text(str(stats['artist']))
            self._title.set_text(str(stats['artist']))
