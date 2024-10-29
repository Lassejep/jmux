import curses

from src.data_models import Event
from src.interfaces import Presenter, View


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
