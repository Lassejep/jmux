import curses
from typing import List, Tuple

from src.data_models import Event
from src.interfaces import Presenter, View


class MultiplexerMenuRenderer(View[Event]):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
    ) -> None:
        """
        A window to show a menu.
        """
        self.presenter: Presenter
        self.size = size
        self.position = position
        self.screen = curses.newpad(256, 256)
        self.screen.keypad(True)
        self.menu_offset = 1
        self.lower_corner = tuple(pos + size for pos, size in zip(position, size))
        self.view_index = 0

    def get_event(self) -> Event:
        """
        Get a command from the user.
        """
        return self._key_to_command(self.screen.getch())

    def _key_to_command(self, key: int) -> Event:
        return {
            ord("q"): Event.EXIT,
            curses.KEY_EXIT: Event.EXIT,
            27: Event.EXIT,
            curses.KEY_UP: Event.MOVE_UP,
            ord("k"): Event.MOVE_UP,
            curses.KEY_DOWN: Event.MOVE_DOWN,
            ord("j"): Event.MOVE_DOWN,
            curses.KEY_LEFT: Event.MOVE_LEFT,
            ord("h"): Event.MOVE_LEFT,
            curses.KEY_RIGHT: Event.MOVE_RIGHT,
            ord("l"): Event.MOVE_RIGHT,
            ord("o"): Event.CREATE_SESSION,
            ord("r"): Event.RENAME_SESSION,
            ord("s"): Event.SAVE_SESSION,
            ord("d"): Event.KILL_SESSION,
            curses.KEY_ENTER: Event.LOAD_SESSION,
            10: Event.LOAD_SESSION,
        }.get(key, Event.UNKNOWN)

    def render(self, items: List[str], cursor_index: int, active: bool) -> None:
        """
        Render the menu.
        """
        self.screen.clear()
        self.screen.addstr(0, 0, "Choose a session:", curses.A_BOLD)
        for item_index, item in enumerate(items):
            self.screen.addstr(item_index + self.menu_offset, 0, item)
        if active:
            self.screen.chgat(cursor_index + self.menu_offset, 0, -1, curses.A_REVERSE)
        self.view_index = max(0, cursor_index - self.size[0] + 3)
        self.screen.refresh(self.view_index, 0, *self.position, *self.lower_corner)
