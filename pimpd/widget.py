from PIL import ImageDraw, Image


class Widget(object):
    def __init__(self, size):
        # type: (Widget, (int, int)) -> None
        self._size = size

    def refresh(self, img, draw, position):
        # type: (Widget, Image, ImageDraw, (int, int)) -> None
        buf = Image.new('1', self._size)
        buf_draw = ImageDraw.Draw(buf)
        self._draw(buf_draw)
        img.paste(buf, position)

    def _draw(self, draw):
        # type: (Widget, ImageDraw) -> None
        pass
