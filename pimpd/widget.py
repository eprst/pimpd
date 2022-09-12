import asyncio
from typing import Tuple

import typing
from PIL import ImageDraw, Image, ImageChops


class Widget(object):
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int]) -> None:
        self._position = position
        self._size = size
        self._draw_border = False
        self._invert = False
        self._need_refresh = True
        self._update_task: typing.Union[asyncio.Task, None] = None

    def set_position(self, position: Tuple[int, int]):
        self._position = position

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    def set_size(self, size: Tuple[int, int]):
        self._size = size

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    def need_refresh(self) -> bool:
        return self._need_refresh

    def set_draw_border(self, draw_border):
        self._draw_border = draw_border

    def set_invert(self, invert):
        self._invert = invert

    def start(self):
        if self._update_task is not None:
            raise "widget already started!"
        self._update_task = asyncio.create_task(self._update_loop())
        pass

    def stop(self):
        if self._update_task is None:
            raise "widget already stopped!"
        self._update_task.cancel()
        self._update_task = None
        pass

    async def _update_loop(self):
        pass

    def refresh(self, img: Image, draw: ImageDraw) -> None:
        buf = Image.new('1', self._size)
        buf_draw = ImageDraw.Draw(buf)
        sz = (max(0, self._size[0] - 1), max(0, self._size[1] - 1))

        self._draw(buf, buf_draw)

        if self._draw_border:
            buf_draw.line([(0, 0), (sz[0], 0), sz, (0, sz[1]), (0, 0)], fill=1)

        if self._invert:
            buf2 = Image.new('1', self._size)
            buf2_draw = ImageDraw.Draw(buf2)
            buf2_draw.rectangle((0, 0, sz[0], sz[1]), outline=255, fill=1)
            buf = ImageChops.subtract(buf2, buf)

        img.paste(buf, self._position)
        self._need_refresh = False

    def _draw(self, img: Image, draw: ImageDraw) -> None:
        pass
