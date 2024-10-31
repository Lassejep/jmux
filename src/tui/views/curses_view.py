import curses

from src.data_models import Event
from src.interfaces import Presenter, View


class CursesView(View[Event]):
    def __init__(self, window: curses.window) -> None:
        """
        A Curses GUI that implements the View interface.
        """
        self.presenter: Presenter[Event, None]
        self.window: curses.window = window
        self.window_size = self.window.getmaxyx()
        self.window.keypad(True)

    def get_event(self) -> Event:
        """
        Capture user input.
        """
        raise NotImplementedError

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
