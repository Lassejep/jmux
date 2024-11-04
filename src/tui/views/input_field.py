import curses
from typing import Tuple

from src.data_models import Key
from src.interfaces import View


class InputFieldRenderer(View[Key]):
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int]):
        self.position = position
        self.size = size
        self.text_field = curses.newpad(size[0], 999)
        self.text_field.keypad(True)
        self.lower_corner = tuple(pos + size for pos, size in zip(position, size))
        self.view_position = (0, 0)

    def get_event(self) -> Key:
        curses.curs_set(1)
        try:
            key = Key(self.text_field.getch())
        except ValueError:
            key = Key.UNKNOWN
        curses.curs_set(0)
        return key

    def render(
        self, text: str, cursor_position: Tuple[int, int], is_error: bool = False
    ) -> None:
        self.text_field.clear()
        if is_error:
            self.text_field.addstr(0, 0, text, curses.A_BOLD | curses.color_pair(1))
        else:
            self.text_field.addstr(0, 0, text)
        self.text_field.move(*cursor_position)
        self.view_position = (
            max(0, cursor_position[0] - self.size[0] + 1),
            max(0, cursor_position[1] - self.size[1] + 1),
        )
        self.text_field.refresh(*self.view_position, *self.position, *self.lower_corner)
