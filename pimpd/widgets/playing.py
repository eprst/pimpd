from typing import Tuple

from PIL import ImageDraw
from PIL import Image
from widget import Widget


class PlayingWidget(Widget):
    STOPPED, PAUSED, PLAYING = (1, 2, 3)

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int]) -> None:
        super(PlayingWidget, self).__init__(position, size)
        self._need_refresh = None
        self._status = PlayingWidget.STOPPED

    @property
    def status(self):
        return self._status

    def set_status(self, status):
        if status != self._status:
            self._need_refresh = True
            self._status = status

    def _draw(self, img: Image, draw: ImageDraw) -> None:
        w = self._size[0]
        h = self._size[1]
        if self._status == PlayingWidget.STOPPED:
            draw.rectangle((0, 0, w, h), outline=1, fill=1)
        elif self._status == PlayingWidget.PAUSED:
            draw.rectangle((0, 0, w, h), outline=0, fill=0)
            draw.rectangle((0, 0, w // 3 - 1, h), outline=1, fill=1)
            draw.rectangle((2 * w // 3, 0, w, h), outline=1, fill=1)
        elif self._status == PlayingWidget.PLAYING:
            draw.rectangle((0, 0, w, h), outline=0, fill=0)
            draw.polygon([
                (0, 0),
                (w, h // 2),
                (0, h - 1)
            ], outline=1, fill=1)
