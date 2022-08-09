import math

from widgets.scrollingtext import ScrollingText
from widget import Widget


class TextList(Widget):
    _text_margin = 1
    _selected = None  # type: None | int

    def __init__(self, position, size, font, empty_items_text):
        super(TextList, self).__init__(position, size)
        self._need_refresh = None
        self._font = font
        self._emtpy_items_text = empty_items_text

        width = size[0]
        height = size[1]
        assert width > 0
        assert height > 0
        text_height = font.getsize("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")[1]
        assert text_height > 0

        num_lines = int(math.ceil(float(height) / (text_height + self._text_margin)))
        self._lines = []
        for i in range(0, num_lines):
            line_y = i * (text_height + self._text_margin)
            self._lines.append(ScrollingText(
                (self._text_margin, line_y),
                (width - 2 * self._text_margin, text_height),
                font,
                ""
            ))

        self._items = []
        self._selected_item = None
        self._on_empty_items()

    def _middle_line(self):
        return self._lines[int((len(self._lines) - 1) / 2)]

    def _on_empty_items(self):
        self._reset_lines()
        self._middle_line().set_text(self._emtpy_items_text)
        self._middle_line().set_scroll(True)
        self._top_line_idx = None
        self._selected = None

    def _reset_lines(self):
        for l in self._lines:
            l.set_text("")
            l.set_invert(False)
            l.set_draw_border(False)
            l.set_scroll(False)

    @property
    def selected(self):
        return self._selected

    def set_selected(self, selected):
        self._selected = max(0, min(selected, len(self._items) - 1))

    def set_items(self, items):
        self._items = items

        if len(items) == 0:
            self._selected = None
            self._on_empty_items()
        else:
            # noinspection PyTypeChecker
            if self._selected is None:
                self._selected = 0
            elif self._selected >= len(items):
                self._selected = len(items) - 1
            self._update_lines()

        self._need_refresh = True

    def select_next(self):
        if self._selected is not None:
            self._selected = (self._selected + 1) % len(self._items)
            self._update_lines()
            self._need_refresh = True

    def select_previous(self):
        if self._selected is not None:
            self._selected -= 1
            if self._selected < 0:
                self._selected = len(self._items) + self._selected
            self._update_lines()
            self._need_refresh = True

    def tick(self):
        if self._selected_item is not None:
            self._selected_item.tick()

    def need_refresh(self):
        if super(TextList, self).need_refresh():
            return True
        return self._selected_item is not None and self._selected_item.need_refresh()

    def _update_lines(self):
        self._reset_lines()
        # 0, 1, 2, ..., k-1
        # 0 <= n <= k // window size
        # 0 <= i <= k
        # find 0 <= s <= k such that:
        # (s + n/2) mod k == i
        # s + n/2 = x*k + i

        k = len(self._items)
        n = min(k, len(self._lines))
        s = self._selected - n / 2 + 1
        # if s < 0:
        #   s += k
        if s < 0:
            s = 0
        elif s + n > k:
            s = k - n

        # make bottom line fully visible if it is selected
        text_height = self._lines[0].size[1]
        num_lines = len(self._lines)
        if k * (text_height + self._text_margin) > self.size[1]:
            if self._selected == k - 1:
                y = self.size[1] - text_height
                for i in range(0, num_lines):
                    line = self._lines[num_lines - i - 1]
                    line.set_position((self._text_margin, y))
                    y -= text_height
                    y -= self._text_margin
            else:
                for i in range(0, num_lines):
                    y = i * (text_height + self._text_margin)
                    line = self._lines[i]
                    line.set_position((self._text_margin, y))

        for i in range(0, n):
            line = self._lines[i]
            line.set_text(self._items[s])
            line.set_scroll(s == self._selected)
            line.set_invert(s == self._selected)
            if s == self._selected:
                self._selected_item = line
            s = (s + 1) % k

    def _draw(self, img, draw):
        super(TextList, self)._draw(img, draw)
        for l in self._lines:
            l.refresh(img, draw)
