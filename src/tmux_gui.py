import curses
import sys
from enum import Enum
from typing import List, Tuple

from src.gui import Presenter, View
from src.session_manager import SessionManager


class Key(Enum):
    ESCAPE = 27
    UP = curses.KEY_UP
    DOWN = curses.KEY_DOWN
    LOWER_Q = ord("q")
    LOWER_J = ord("j")
    LOWER_K = ord("k")


class TmuxPresenter(Presenter):
    def __init__(self, view: View, session_manager: SessionManager):
        self.view = view
        self.session_manager = session_manager

    def run(self) -> None:
        self.view.start()

    def _get_sessions(self) -> List[str]:
        sessions_dir = self.session_manager.file_handler.sessions_folder
        return [session_file.stem for session_file in sessions_dir.iterdir()]

    def format_sessions(self) -> List[Tuple[int, int, str]]:
        sessions = self._get_sessions()
        return [
            (index + 1, 0, f"{index + 1}. {session}")
            for index, session in enumerate(sessions)
        ]

    def handle_input(self, key: int) -> None:
        match key:
            case Key.LOWER_Q.value | Key.ESCAPE.value:
                sys.exit(0)
            case Key.LOWER_K.value | Key.UP.value:
                self.view.cursor_up()
            case Key.LOWER_J.value | Key.DOWN.value:
                self.view.cursor_down()
            case _:
                pass


class TmuxView(View):
    def __init__(self, session_manager: SessionManager):
        self.presenter: Presenter = TmuxPresenter(self, session_manager)

    def start(self) -> None:
        curses.wrapper(self.start_curses)

    def start_curses(self, stdscr) -> None:
        self.screen = stdscr
        curses.start_color()
        curses.use_default_colors()
        curses.cbreak(True)
        curses.noecho()
        stdscr.keypad(True)
        self.show_menu()

    def show_menu(self) -> None:
        self.screen.clear()
        self.screen.addstr(0, 0, "Select an action:")
        for session in self.presenter.format_sessions():
            self.screen.addstr(*session)
        self.screen.refresh()
        while True:
            key = self.screen.getch()
            self.presenter.handle_input(key)
            self.screen.refresh()

    def cursor_down(self) -> None:
        cursor_y, cursor_x = curses.getsyx()
        if cursor_y == len(self.presenter.format_sessions()):
            return
        self.screen.move(cursor_y + 1, cursor_x)

    def cursor_up(self) -> None:
        cursor_y, cursor_x = curses.getsyx()
        if cursor_y == 1:
            return
        self.screen.move(cursor_y - 1, cursor_x)
