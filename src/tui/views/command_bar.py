import curses
from typing import Tuple

from src.data_models import Event
from src.interfaces import Presenter, View


class CommandBarRenderer(View):
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
