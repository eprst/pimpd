from PIL import ImageDraw

from widget import Widget


class ProgressBar(Widget):
    def __init__(self, position, size, max_value):
        # type: (ProgressBar, (int, int), (int, int), float) -> None
        super(ProgressBar, self).__init__(position, size)
        self._max_value = max_value
        self._value = 0

    def set_value(self, value):
        # type: (float) -> None
        assert value >= 0 and value <= self._max_value
        self._value = value

    def _draw(self, img, draw):
        # type: (ProgressBar, ImageDraw) -> None
        len = self._value * self._size[0] / self._max_value
        draw.rectangle((0,0,self._size[0],self._size[1]), outline=0, fill=0)
        draw.rectangle((0,0,len,self._size[1]), outline=1, fill=1)

