from PIL import ImageDraw, ImageFont

from widget import Widget


class ScrollingText(Widget):
    MAX_START_PAUSE = 10

    def __init__(self, size, font, text):
        # type: (ScrollingText, (int, int), ImageFont, str) -> None
        super(ScrollingText, self).__init__(size)
        self._font = font
        self.set_text(text)

    # noinspection PyAttributeOutsideInit
    def set_text(self, text):
        self._text = text
        self._start_pause = 0
        self._reversing = False
        self._offset = 0
        self._text_size = self._font.getsize(text)

    def _max_offset(self):
        return max(0, self._text_size[0] - self._size[0])

    def _update_offset(self):
        if self._start_pause < self.MAX_START_PAUSE:
            self._start_pause += 1
        else:
            if self._reversing:
                self._offset -= 1
                if self._offset <= 0:
                    self._offset = 0
                    self._start_pause = 0
                    self._reversing = False
            else:
                self._offset += 1
                max_offset = self._max_offset()
                if self._offset >= max_offset:
                    self._offset = max_offset
                    self._reversing = True

    def _draw(self, draw):
        # type: (ScrollingText, ImageDraw) -> None
        super(ScrollingText, self)._draw(draw)
        self._update_offset()
        draw.text((-self._offset, 0), self._text, font=self._font, fill=1)
