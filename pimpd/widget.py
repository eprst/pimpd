from PIL import ImageDraw, Image, ImageChops


class Widget(object):
    def __init__(self, position, size):
        # type: (Widget, (int, int), (int, int)) -> None
        self._position = position
        self._size = size
        self._draw_border = False
        self._invert = False

    def set_position(self, position):
        self._position = position

    def set_size(self, size):
        self._size = size

    def set_draw_border(self, draw_border):
        self._draw_border = draw_border

    def set_invert(self, invert):
        self._invert = invert

    def refresh(self, img, draw):
        # type: (Widget, Image, ImageDraw) -> None
        buf = Image.new('1', self._size)
        buf_draw = ImageDraw.Draw(buf)
        self._draw(buf, buf_draw)
        if self._draw_border:
            buf_draw.rectangle((0, 0), self._size, outline=255, fill=0)

        if self._invert:
            buf = ImageChops.invert(buf)

        img.paste(buf, self._position)

    def _draw(self, img, draw):
        # type: (Widget, Image, ImageDraw) -> None
        pass
