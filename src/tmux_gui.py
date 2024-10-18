import curses
import sys
from enum import Enum
from typing import Callable, Concatenate, List, ParamSpec, Tuple, TypeVar

from src.gui import Presenter, View
from src.session_manager import SessionManager


class InputKeys(Enum):
    ESCAPE = 27
    ENTER = 10
    UP = curses.KEY_UP
    DOWN = curses.KEY_DOWN
    LOWER_Q = ord("q")
    LOWER_J = ord("j")
    LOWER_K = ord("k")


class TmuxPresenter(Presenter):
    """
    Presenter for the GUI.
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

    def show_session_menu(self):
        """
        Format the sessions for display.
        """
        self._update_saved_sessions()
        if len(self.saved_sessions) > 0:
            self.position = 1
        sessions = [
            (index + 1, 0, f"{index + 1}. {session}")
            for index, session in enumerate(self.saved_sessions)
        ]
        self.view.show_menu(sessions)

    def handle_input(self, key: int) -> None:
        """
        Handle user input.
        """
        match key:
            case InputKeys.LOWER_Q.value | InputKeys.ESCAPE.value:
                self.exit_program()
            case InputKeys.LOWER_K.value | InputKeys.UP.value:
                self._move_cursor_up()
            case InputKeys.LOWER_J.value | InputKeys.DOWN.value:
                self._move_cursor_down()
            case InputKeys.ENTER.value:
                self.load_session()
            case _:
                error_message = f"Invalid key code: {key}"
                self.view.show_error(error_message)

    def exit_program(self) -> None:
        self.view.stop()
        sys.exit(0)

    def _move_cursor_up(self) -> None:
        if self.position > 1:
            self.position -= 1
            self.view.cursor_up()

    def _move_cursor_down(self) -> None:
        if self.position < len(self.saved_sessions):
            self.position += 1
            self.view.cursor_down()

    def load_session(self) -> None:
        """
        Load the selected session.
        """
        self.saved_sessions
        if len(self.saved_sessions) == 0:
            self.view.show_error("No sessions to load")
            return
        session_name = self.saved_sessions[self.position - 1]
        try:
            self.session_manager.load_session(session_name)
            self.exit_program()
        except ValueError as e:
            self.view.show_error(str(e))


Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")


class CursesGUI(View):
    """
    A Curses GUI that implements the View interface.
    """

    def __init__(self, session_manager: SessionManager):
        self.presenter: Presenter = TmuxPresenter(self, session_manager)

    @staticmethod
    def _static_cursor(
        func: Callable[Concatenate["CursesGUI", Params], ReturnType]
    ) -> Callable[Concatenate["CursesGUI", Params], ReturnType]:
        def inner(
            self: "CursesGUI", *args: Params.args, **kwargs: Params.kwargs
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
        self.screen: curses.window = stdscr.subpad(0, 0)
        self._init_colors()
        curses.cbreak(True)
        curses.noecho()
        curses.curs_set(0)
        curses.set_escdelay(50)
        self.screen.keypad(True)
        self.presenter.show_session_menu()

    def _init_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        self.error_color = curses.color_pair(1)

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
        size = self.screen.getmaxyx()
        self.screen.addstr(size[0] - 1, 0, message, self.error_color)
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
