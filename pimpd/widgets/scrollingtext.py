import asyncio
from typing import Tuple

from PIL import ImageDraw, ImageFont, Image
from widget import Widget
import logging


class ScrollingText(Widget):
    SCROLL_DELAY = 0.2

    def __init__(self, position: Tuple[int, int], size: Tuple[int, int], font: ImageFont, text: str) -> None:
        super(ScrollingText, self).__init__(position, size)
        self._reversing = None
        self._offset = None
        self._font = font
        self._text: str = ""
        self._text_size = None
        self.set_text(text)
        self._scroll = True
        self._scroll_event = asyncio.Event()

    # noinspection PyAttributeOutsideInit
    def set_text(self, text: str):
        if text != self._text:
            try:
                self._text = text
                self._pause = 0
                self._reversing = False
                self._offset = 0
                self._text_size = self._font.getsize(text)
                self._need_refresh = True
                if self._size[1] < self._text_size[1]:
                    logging.warning(u"Warning! widget height {} is smaller than font height {} (text: '{}')".format(
                        self._size[1], self._text_size[1], text
                    ))
            except IOError:
                self.set_text(u"err")  # getting 'IOError: invalid composite glyph' periodically

    def text(self) -> str:
        return self._text

    def set_scroll(self, scroll: bool):
        # print("set_scroll: ", scroll, " : ", self._text)
        self._scroll = scroll
        self.set_text(self._text)  # reset scrolling
        if scroll:
            self._scroll_event.set()
        else:
            self._scroll_event.clear()

    def _max_offset(self) -> int:
        return max(0, self._text_size[0] - self._size[0])

    async def _update_loop(self):
        try:
            while True:
                if self._scroll:
                    print("scrolling: ", self._text, ", offset: ", self._offset)
                    await asyncio.sleep(self.SCROLL_DELAY)
                    if self._reversing:
                        self._offset -= 1
                        if self._offset <= 0:
                            self._offset = 0
                            self._reversing = False
                    else:
                        self._offset += 1
                        max_offset = self._max_offset()
                        if self._offset >= max_offset:
                            self._offset = max_offset
                            self._reversing = True

                    self._need_refresh = True
                else:
                    print("not scrolling: ", self._text)
                    await self._scroll_event.wait()
        except asyncio.CancelledError:
            print("cancelled scroll: ", self._text)
            pass

    def _draw(self, img: Image, draw: ImageDraw) -> None:
        super(ScrollingText, self)._draw(img, draw)
        # self._update_offset()
        if self._text_size is not None:
            y_offset = max(0, (self._size[1] - self._text_size[1])/2)
            draw.text((-self._offset, y_offset), self._text, font=self._font, fill=1)
