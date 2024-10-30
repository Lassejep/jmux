import curses
from typing import List, Tuple

from src.data_models import Event
from src.interfaces import Presenter, View


class MenuRenderer(View[Event]):
    def __init__(
        self,
        position: Tuple[int, int],
        size: Tuple[int, int],
        title: str,
    ) -> None:
        """
        A window to show a menu.
        """
        self.presenter: Presenter
        self.size = size
        self.position = position
        self.title = title
        self.screen = curses.newpad(*size)
        self.screen.keypad(True)
        self.menu_offset = 1

    def _refresh(self) -> None:
        lower_corner = (pos + size for pos, size in zip(self.position, self.size))
        self.screen.refresh(0, 0, *self.position, *lower_corner)

    def _clear(self) -> None:
        self.screen.clear()
        self._refresh()

    def render(self, items: List[str], cursor_index: int, active: bool) -> None:
        """
        Render the menu.
        """
        self._clear()
        self.screen.addstr(0, 0, self.title, curses.A_BOLD)
        for item_index, item in enumerate(items):
            self.screen.addstr(item_index + self.menu_offset, 0, item)
        if active:
            self.screen.chgat(cursor_index + self.menu_offset, 0, -1, curses.A_REVERSE)
        self._refresh()

    def get_command(self) -> Event:
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
            ord("d"): Event.DELETE_SESSION,
            ord("s"): Event.SAVE_SESSION,
            ord("x"): Event.KILL_SESSION,
            curses.KEY_ENTER: Event.LOAD_SESSION,
            10: Event.LOAD_SESSION,
        }.get(key, Event.UNKNOWN)

    def get_input(self, input_prompt: str) -> str:
        """
        Show `input_prompt` and return a string based on user input.
        """
        raise NotImplementedError

    def get_confirmation(self, confirmation_prompt: str) -> bool:
        """
        Show `confirmation_prompt` and return a boolean based on user input.
        """
        raise NotImplementedError

    def show_message(self, message: str) -> None:
        """
        Show a message to the user.
        """
        raise NotImplementedError
