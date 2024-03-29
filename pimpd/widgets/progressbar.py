from PIL import Image, ImageDraw

from widget import Widget


class ProgressBar(Widget):
    def __init__(self, position: (int, int), size: (int, int), max_value: float) -> None:
        super(ProgressBar, self).__init__(position, size)
        self._max_value = max_value
        self._value = 0

    def set_value(self, value: float) -> None:
        assert 0 <= value <= self._max_value, "assertion failed: 0 <= %r <= %r" % (value, self._max_value)
        self._need_refresh |= (value != self._value)
        self._value = value

    def _draw(self, img: Image, draw: ImageDraw) -> None:
        _len = self._value * self._size[0] / self._max_value
        draw.rectangle((0, 0, self._size[0], self._size[1]), outline=0, fill=0)
        draw.rectangle((0, 0, _len, self._size[1]), outline=1, fill=1)
