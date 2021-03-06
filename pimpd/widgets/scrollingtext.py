from PIL import ImageDraw, ImageFont
from widget import Widget
import logging


class ScrollingText(Widget):
    MAX_PAUSE = 10

    def __init__(self, position, size, font, text):
        # type: (ScrollingText, (int, int), (int, int), ImageFont, str) -> None
        super(ScrollingText, self).__init__(position, size)
        self._font = font
        self._text = None
        self.set_text(text)
        self._scroll = True

    # noinspection PyAttributeOutsideInit
    def set_text(self, text):
        # temp debugging
        # if isinstance(text, unicode) != isinstance(self._text,unicode):
        #    print("my text: '{}'(unicode: {}), new text: '{}'(unicode: {})".format(self._text, isinstance(self._text,unicode),text,isinstance(text,unicode)))
        if text != self._text:
            try:
                self._text = text
                self._pause = 0
                self._reversing = False
                self._offset = 0
                self._text_size = self._font.getsize(text)
                self._need_refresh = True
                if self._size[1] < self._text_size[1]:
                    logging.warning(u"Warning! widget height {} is smaller than font height {} (text: '{}')".format(self._size[1], self._text_size[1], text))
            except IOError:
                self.set_text(u"err") # getting 'IOError: invalid composite glyph' periodically

    def set_scroll(self, scroll):
        self._scroll = scroll
        self.set_text(self._text) # reset scrolling

    def _max_offset(self):
        return max(0, self._text_size[0] - self._size[0])

    def tick(self):
        prev_offset = self._offset
        if self._scroll:
            if self._pause < self.MAX_PAUSE:
                self._pause += 1
            else:
                if self._reversing:
                    self._offset -= 1
                    if self._offset <= 0:
                        self._offset = 0
                        self._pause = 0
                        self._reversing = False
                else:
                    self._offset += 1
                    max_offset = self._max_offset()
                    if self._offset >= max_offset:
                        self._offset = max_offset
                        self._reversing = True
                        self._pause = 0

        self._need_refresh |= self._offset != prev_offset


    def _draw(self, img, draw):
        # type: (ScrollingText, ImageDraw) -> None
        super(ScrollingText, self)._draw(img, draw)
        # self._update_offset()
        y_offset = max(0, (self._size[1] - self._text_size[1])/2)
        draw.text((-self._offset, y_offset), self._text, font=self._font, fill=1)
