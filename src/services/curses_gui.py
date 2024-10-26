import curses
from typing import List, Tuple

from src.interfaces import Presenter, View
from src.models import Event


class CursesView(View):
    def __init__(self, window: curses.window) -> None:
        """
        A Curses GUI that implements the View interface.
        """
        self.presenter: Presenter
        self.window: curses.window = window
        self.window_size = self.window.getmaxyx()
        self.window.keypad(True)

    def render(self) -> None:
        """
        Render the view.
        """
        self.window.border()
        self.window.hline(
            self.window_size[0] - 3, 0, curses.ACS_HLINE, self.window_size[1]
        )
        self.window.addch(self.window_size[0] - 3, 0, curses.ACS_LTEE)
        self.window.addch(
            self.window_size[0] - 3, self.window_size[1] - 1, curses.ACS_RTEE
        )
        self.window.vline(
            0, self.window_size[1] // 2, curses.ACS_VLINE, self.window_size[0] - 3
        )
        self.window.addch(0, self.window_size[1] // 2, curses.ACS_TTEE)
        self.window.addch(
            self.window_size[0] - 3, self.window_size[1] // 2, curses.ACS_BTEE
        )
        self.window.refresh()

    def get_command(self) -> Event:
        """
        Capture user input.
        """
        raise NotImplementedError

    def get_confirmation(self, confirmation_prompt: str) -> bool:
        """
        Show the `message` and get return the key pressed.
        """
        raise NotImplementedError

    def get_input(self, input_prompt: str) -> str:
        """
        Show the `message` and get return the input.
        """
        raise NotImplementedError

    def show_message(self, message: str) -> None:
        """
        Show an error message.
        """
        raise NotImplementedError


class MenuRenderer(View):
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

    def _refresh(self) -> None:
        lower_corner = (pos + size for pos, size in zip(self.position, self.size))
        self.screen.refresh(0, 0, *self.position, *lower_corner)

    def _clear(self) -> None:
        self.screen.clear()
        self._refresh()

    def render(self, items: List[str], cursor: int) -> None:
        """
        Render the menu.
        """
        self._clear()
        self.screen.addstr(0, 0, self.title, curses.A_BOLD)
        offset = 1
        for index, item in enumerate(items):
            self.screen.addstr(index + offset, 0, item)
        self.screen.move(cursor + offset, 0)
        self.screen.chgat(cursor + offset, 0, -1, curses.A_REVERSE)
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


class MessageWindow(View):
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int]) -> None:
        """
        A window to show messages.
        """
        self.presenter: Presenter
        self.size = size
        self.position = position
        self.screen = curses.newpad(*self.size)
        self.screen.keypad(True)

    def _refresh(self) -> None:
        lower_corner = (pos + size for pos, size in zip(self.position, self.size))
        self.screen.refresh(0, 0, *self.position, *lower_corner)

    def _clear(self) -> None:
        """
        Clear the screen.
        """
        self.screen.clear()
        self._refresh()

    def render(self, message: str) -> None:
        """
        Render the message.
        """
        self._clear()
        self.screen.addstr(0, 0, message, curses.A_NORMAL)
        self._refresh()

    def get_command(self) -> Event:
        """
        Get a command from the user.
        """
        return Event.UNKNOWN

    def get_input(self, input_prompt: str) -> str:
        """
        Get user input.
        """
        self.render(input_prompt)
        curses.echo()
        curses.curs_set(1)
        input = self.screen.getstr().decode("utf-8")
        curses.curs_set(0)
        curses.noecho()
        self._clear()
        return input

    def get_confirmation(self, confirmation_prompt: str) -> bool:
        """
        Show a confirmation message.
        """
        self.render(confirmation_prompt)
        confirmation = self.screen.getch() in [ord("y"), ord("Y")]
        self._clear()
        return confirmation

    def show_message(self, message: str) -> None:
        """
        Show a message.
        """
        self._clear()
        self.screen.addstr(0, 0, message, curses.color_pair(1))
        self._refresh()
