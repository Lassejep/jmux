import curses
from typing import Callable, Concatenate, List, ParamSpec, Tuple, TypeVar

from src.interfaces import Model, Presenter, View
from src.services.jmux_presenter import JmuxPresenter

Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


class CursesGui(View):
    def __init__(self, model: Model):
        """
        A Curses GUI that implements the View interface.
        """
        self.presenter: Presenter = JmuxPresenter(self, model)

    @staticmethod
    def _static_cursor(
        func: Callable[Concatenate["CursesGui", Params], ReturnType]
    ) -> Callable[Concatenate["CursesGui", Params], ReturnType]:
        def inner(
            self: "CursesGui", *args: Params.args, **kwargs: Params.kwargs
        ) -> ReturnType:
            cursor_pos = self.screen.getyx()
            result = func(self, *args, **kwargs)
            self.screen.move(*cursor_pos)
            return result

        return inner

    def start(self) -> None:
        """
        Start the view.
        """
        curses.wrapper(self._start_curses)

    def stop(self) -> None:
        """
        Stop the view.
        """
        self.show_error("Exiting...")

    def _start_curses(self, stdscr) -> None:
        curses.cbreak(True)
        curses.noecho()
        curses.curs_set(0)
        curses.set_escdelay(50)
        self._init_colors()
        self._init_screen(stdscr)
        self.presenter.running_sessions_menu()

    def _init_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        self.error_color = curses.color_pair(1)

    def _init_screen(self, stdscr) -> None:
        size = stdscr.getmaxyx()
        self.screen: curses.window = stdscr.subpad(0, 0)
        self.screen.keypad(True)
        self.msgbox = self.screen.subpad(1, size[1] - 1, size[0] - 1, 0)

    def show_menu(self, sessions: List[Tuple[int, int, str]]) -> None:
        """
        Show the menu.
        """
        self.screen.clear()
        self.screen.addstr(0, 0, "Select an action:")
        for session in sessions:
            self.screen.addstr(*session)
        self.screen.move(1, 0)
        self.screen.chgat(1, 0, -1, curses.A_REVERSE)
        self.screen.refresh()
        while True:
            key = self.screen.getch()
            self.presenter.handle_input(key)
            self.screen.refresh()

    @_static_cursor
    def show_error(self, message: str) -> None:
        """
        Show an error message.
        """
        self.msgbox.clear()
        self.msgbox.addstr(message, self.error_color)
        self.msgbox.refresh()

    def cursor_down(self) -> None:
        """
        Move the cursor down.
        """
        cursor_y, cursor_x = curses.getsyx()
        new_y = cursor_y + 1
        self._move_highlight(new_y)
        self.screen.move(new_y, cursor_x)

    def cursor_up(self) -> None:
        """
        Move the cursor up.
        """
        cursor_y, cursor_x = curses.getsyx()
        new_y = cursor_y - 1
        self._move_highlight(new_y)
        self.screen.move(new_y, cursor_x)

    def _move_highlight(self, new_y: int) -> None:
        cursor_y, cursor_x = curses.getsyx()
        self.screen.chgat(cursor_y, 0, -1, curses.A_NORMAL)
        self.screen.chgat(new_y, 0, -1, curses.A_REVERSE)

    def get_confirmation(self, message: str) -> int:
        """
        Show the `message` and get return the key pressed.
        """
        self.msgbox.clear()
        self.msgbox.addstr(message)
        self.msgbox.refresh()
        return self.msgbox.getch()
