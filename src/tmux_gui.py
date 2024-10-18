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
    """
    Presenter for the TmuxView.
    """

    def __init__(self, view: View, session_manager: SessionManager):
        self.view = view
        self.session_manager = session_manager
        self.position = 0

    def run(self) -> None:
        """
        Start the presenter.
        """
        self.view.start()

    def _get_sessions(self) -> List[str]:
        sessions_dir = self.session_manager.file_handler.sessions_folder
        return [session_file.stem for session_file in sessions_dir.iterdir()]

    def format_sessions(self) -> List[Tuple[int, int, str]]:
        """
        Format the sessions for display.
        """
        sessions = self._get_sessions()
        if len(sessions) > 0:
            self.position = 1
        return [
            (index + 1, 0, f"{index + 1}. {session}")
            for index, session in enumerate(sessions)
        ]

    def handle_input(self, key: int) -> None:
        """
        Handle user input.
        """
        match key:
            case Key.LOWER_Q.value | Key.ESCAPE.value:
                sys.exit(0)
            case Key.LOWER_K.value | Key.UP.value:
                if self.position > 1:
                    self.position -= 1
                    self.view.cursor_up()
            case Key.LOWER_J.value | Key.DOWN.value:
                if self.position < len(self._get_sessions()):
                    self.position += 1
                    self.view.cursor_down()
            case _:
                pass


class TmuxView(View):
    """
    View for the TmuxPresenter.
    """

    def __init__(self, session_manager: SessionManager):
        self.presenter: Presenter = TmuxPresenter(self, session_manager)

    def start(self) -> None:
        """
        Start the view.
        """
        curses.wrapper(self.start_curses)

    def start_curses(self, stdscr) -> None:
        """
        Set starting values for the curses window.
        """
        self.screen: curses.window = stdscr
        curses.start_color()
        curses.use_default_colors()
        curses.cbreak(True)
        curses.noecho()
        curses.curs_set(0)
        stdscr.keypad(True)
        self.show_menu()

    def show_menu(self) -> None:
        """
        Show the menu.
        """
        self.screen.clear()
        self.screen.addstr(0, 0, "Select an action:")
        for session in self.presenter.format_sessions():
            self.screen.addstr(*session)
        self.screen.move(1, 0)
        self.screen.chgat(1, 0, -1, curses.A_REVERSE)
        self.screen.refresh()
        while True:
            key = self.screen.getch()
            self.presenter.handle_input(key)
            self.screen.refresh()

    def cursor_down(self) -> None:
        """
        Move the cursor down.
        """
        cursor_y, cursor_x = curses.getsyx()
        new_y = cursor_y + 1
        self._highlight_selected(new_y)
        self.screen.move(new_y, cursor_x)

    def cursor_up(self) -> None:
        """
        Move the cursor up.
        """
        cursor_y, cursor_x = curses.getsyx()
        new_y = cursor_y - 1
        self._highlight_selected(new_y)
        self.screen.move(new_y, cursor_x)

    def _highlight_selected(self, new_y: int) -> None:
        cursor_y, cursor_x = curses.getsyx()
        self.screen.chgat(cursor_y, 0, -1, curses.A_NORMAL)
        self.screen.chgat(new_y, 0, -1, curses.A_REVERSE)
