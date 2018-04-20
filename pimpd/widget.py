from PIL import ImageDraw, Image


class Widget(object):
    def __init__(self, position, size):
        # type: (Widget, (int, int), (int, int)) -> None
        self._position = position
        self._size = size

    def set_position(self, position):
        self._position = position

    def set_size(self, size):
        self._size = size

    def refresh(self, img, draw):
        # type: (Widget, Image, ImageDraw) -> None
        buf = Image.new('1', self._size)
        buf_draw = ImageDraw.Draw(buf)
        self._draw(buf_draw)
        img.paste(buf, self._position)

    def _draw(self, draw):
        # type: (Widget, ImageDraw) -> None
        pass
