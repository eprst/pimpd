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

    @property
    def position(self):
        return self._position

    def set_size(self, size):
        self._size = size

    @property
    def size(self):
        return self._size

    def set_draw_border(self, draw_border):
        self._draw_border = draw_border

    def set_invert(self, invert):
        self._invert = invert

    def refresh(self, img, draw):
        # type: (Widget, Image, ImageDraw) -> None
        buf = Image.new('1', self._size)
        buf_draw = ImageDraw.Draw(buf)
        sz = (max(0, self._size[0] - 1), max(0, self._size[1] - 1))
        
        self._draw(buf, buf_draw)

        if self._draw_border:
            buf_draw.line([(0, 0), (sz[0], 0), sz, (0, sz[1]), (0, 0)], fill=1)

        if self._invert:
            buf2 = Image.new('1', self._size)
            buf2_draw = ImageDraw.Draw(buf2)
            buf2_draw.rectangle([(0, 0), sz], outline=255, fill=1)
            buf = ImageChops.subtract(buf2, buf)

        img.paste(buf, self._position)

    def _draw(self, img, draw):
        # type: (Widget, Image, ImageDraw) -> None
        pass
