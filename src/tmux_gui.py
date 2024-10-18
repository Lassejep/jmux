import curses
import sys
from enum import Enum
from typing import Callable, Concatenate, List, ParamSpec, Tuple, TypeVar

from src.gui import Presenter, View
from src.session_manager import SessionManager


class Key(Enum):
    ESCAPE = 27
    ENTER = 10
    UP = curses.KEY_UP
    DOWN = curses.KEY_DOWN
    LOWER_Q = ord("q")
    LOWER_J = ord("j")
    LOWER_K = ord("k")


class TmuxPresenter(Presenter):
    """
    Presenter for the TmuxView.
    """

    def __init__(self, view: View, session_manager: SessionManager):
        self.view = view
        self.session_manager = session_manager
        self.position = 0
        self._update_saved_sessions()

    def run(self) -> None:
        """
        Start the presenter.
        """
        self.view.start()

    def _update_saved_sessions(self):
        sessions_dir = self.session_manager.file_handler.sessions_folder
        self.saved_sessions = [
            session_file.stem for session_file in sessions_dir.iterdir()
        ]

    def show_session_menu(self) -> List[Tuple[int, int, str]]:
        """
        Format the sessions for display.
        """
        self._update_saved_sessions()
        if len(self.saved_sessions) > 0:
            self.position = 1
        return [
            (index + 1, 0, f"{index + 1}. {session}")
            for index, session in enumerate(self.saved_sessions)
        ]

    def handle_input(self, key: int) -> None:
        """
        Handle user input.
        """
        match key:
            case Key.LOWER_Q.value | Key.ESCAPE.value:
                self._exit_program()
            case Key.LOWER_K.value | Key.UP.value:
                self._move_cursor_up()
            case Key.LOWER_J.value | Key.DOWN.value:
                self._move_cursor_down()
            case Key.ENTER.value:
                self._load_session()
            case _:
                error_message = f"Invalid key code: {key}"
                self.view.show_error(error_message)

    def _exit_program(self) -> None:
        sys.exit(0)

    def _move_cursor_up(self) -> None:
        if self.position > 1:
            self.position -= 1
            self.view.cursor_up()

    def _move_cursor_down(self) -> None:
        if self.position < len(self.saved_sessions):
            self.position += 1
            self.view.cursor_down()

    def _load_session(self) -> None:
        self.saved_sessions
        if len(self.saved_sessions) == 0:
            self.view.show_error("No sessions to load")
            return
        session_name = self.saved_sessions[self.position - 1]
        try:
            self.session_manager.load_session(session_name)
            sys.exit(0)
        except ValueError as e:
            self.view.show_error(str(e))


Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


class TmuxView(View):
    """
    View for the TmuxPresenter.
    """

    def __init__(self, session_manager: SessionManager):
        self.presenter: Presenter = TmuxPresenter(self, session_manager)

    @staticmethod
    def _static_cursor(
        func: Callable[Concatenate["TmuxView", Params], ReturnType]
    ) -> Callable[Concatenate["TmuxView", Params], ReturnType]:
        def inner(
            self: "TmuxView", *args: Params.args, **kwargs: Params.kwargs
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

    def _start_curses(self, stdscr) -> None:
        self.screen: curses.window = stdscr
        self._init_colors()
        curses.use_default_colors()
        curses.cbreak(True)
        curses.noecho()
        curses.curs_set(0)
        stdscr.keypad(True)
        self.show_menu()

    def _init_colors(self) -> None:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.error_color = curses.color_pair(1)

    def show_menu(self) -> None:
        """
        Show the menu.
        """
        self.screen.clear()
        self.screen.addstr(0, 0, "Select an action:")
        for session in self.presenter.show_session_menu():
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
        size = self.screen.getmaxyx()
        self.screen.addstr(size[0] - 2, 0, message, self.error_color)
        self.screen.refresh()

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
