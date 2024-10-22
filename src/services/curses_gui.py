import curses
from typing import Dict, List

from src.interfaces import Model, Presenter, View
from src.models import Commands
from src.services.curses_presenter import CursesPresenter


class CursesGui(View):
    def __init__(self, model: Model) -> None:
        """
        A Curses GUI that implements the View interface.
        """
        self.presenter: Presenter = CursesPresenter(self, model)
        self.running: bool = False
        self.commands = self._init_commands()

    def _init_commands(self) -> Dict[int, Commands]:
        command_to_keys = {
            Commands.EXIT: [ord("q"), 27],
            Commands.MOVE_UP: [curses.KEY_UP, ord("k")],
            Commands.MOVE_DOWN: [curses.KEY_DOWN, ord("j")],
            Commands.MOVE_LEFT: [curses.KEY_LEFT, ord("h")],
            Commands.MOVE_RIGHT: [curses.KEY_RIGHT, ord("l")],
            Commands.CREATE_SESSION: [ord("o")],
            Commands.SAVE_SESSION: [ord("s")],
            Commands.RENAME_SESSION: [ord("r")],
            Commands.DELETE_SESSION: [ord("d")],
            Commands.LOAD_SESSION: [curses.KEY_ENTER, 10],
        }
        key_to_command = {}
        for command, keys in command_to_keys.items():
            for key in keys:
                key_to_command[key] = command
        return key_to_command

    def start(self) -> None:
        """
        Start the view.
        """
        self.running = True
        curses.wrapper(self._start_curses)

    def _start_curses(self, stdscr) -> None:
        curses.cbreak(True)
        curses.noecho()
        curses.curs_set(0)
        curses.set_escdelay(50)
        self._init_colors()
        self._init_screens(stdscr)
        self.presenter.run()

    def _init_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        self.error_color = curses.color_pair(1)

    def _init_screens(self, window) -> None:
        self.window_size = window.getmaxyx()
        self.multiplexer_menu = MultiplexerMenu(window)
        self.message_screen = MessageWindow(window)
        self._draw_borders(window)

    def _draw_borders(self, window: curses.window) -> None:
        window.border()
        window.hline(self.window_size[0] - 3, 0, curses.ACS_HLINE, self.window_size[1])
        window.addch(self.window_size[0] - 3, 0, curses.ACS_LTEE)
        window.addch(self.window_size[0] - 3, self.window_size[1] - 1, curses.ACS_RTEE)
        window.vline(
            0, self.window_size[1] // 2, curses.ACS_VLINE, self.window_size[0] - 3
        )
        window.addch(0, self.window_size[1] // 2, curses.ACS_TTEE)
        window.addch(self.window_size[0] - 3, self.window_size[1] // 2, curses.ACS_BTEE)
        window.refresh()

    def stop(self) -> None:
        """
        Stop the view.
        """
        self.running = False
        self.show_error("Exiting...")

    def get_input(self) -> Commands:
        """
        Get user input.
        """
        return self.commands.get(self.multiplexer_menu.screen.getch(), Commands.UNKNOWN)

    def show_menu(self, sessions: List[str]) -> None:
        """
        Show the menu.
        """
        self.multiplexer_menu.show_menu(sessions, self.presenter.position)
        self.multiplexer_menu._refresh()

    def show_error(self, message: str) -> None:
        """
        Show an error message.
        """
        self.message_screen.show_message(message, self.error_color)

    def cursor_down(self) -> None:
        """
        Move the cursor down.
        """
        self.multiplexer_menu._move_down()

    def cursor_up(self) -> None:
        """
        Move the cursor up.
        """
        self.multiplexer_menu._move_up()

    def get_confirmation(self, message: str) -> bool:
        """
        Show the `message` and get return the key pressed.
        """
        self.message_screen.show_message(message)
        return self.message_screen.get_confirmation()

    def create_new_session(self) -> str:
        """
        Show a prompt to create a new session and return the name of the session.
        """
        self.message_screen.show_message("Enter a name for the new session: ")
        return self.message_screen.get_input()

    def rename_session(self, session_name: str) -> str:
        """
        Show a prompt to rename a session and return the new name.
        """
        self.message_screen.show_message(f"Enter a new name for {session_name}: ")
        return self.message_screen.get_input()


class MessageWindow:
    def __init__(self, window: curses.window) -> None:
        """
        A window to show messages.
        """
        self.window = window
        self.window_size = window.getmaxyx()
        self.size = (1, self.window_size[1] - 2)
        self.position = (self.window_size[0] - 2, 1)
        self.screen = curses.newpad(*self.size)
        self.screen.keypad(True)

    def _refresh(self) -> None:
        lower_corner = (pos + size for pos, size in zip(self.position, self.size))
        self.screen.refresh(0, 0, *self.position, *lower_corner)

    def clear(self) -> None:
        """
        Clear the screen.
        """
        self.screen.clear()
        self._refresh()

    def show_message(self, message: str, color: int = curses.A_NORMAL) -> None:
        """
        Show a message.
        """
        self.screen.clear()
        self.screen.addstr(message, color)
        self._refresh()

    def get_confirmation(self) -> bool:
        """
        Show a confirmation message.
        """
        confirmation = self.screen.getch() in [ord("y"), ord("Y")]
        self.clear()
        return confirmation

    def get_input(self) -> str:
        """
        Get user input.
        """
        curses.echo()
        curses.curs_set(1)
        input = self.screen.getstr().decode("utf-8")
        curses.curs_set(0)
        curses.noecho()
        self.clear()
        return input


class MultiplexerMenu:
    def __init__(self, window: curses.window) -> None:
        """
        A window to show a multiplexer menu.
        """
        self.window = window
        self.window_size = window.getmaxyx()
        self.size = (self.window_size[0] - 4, (self.window_size[1] - 2) // 2)
        self.position = (1, 1)
        self.screen = curses.newpad(*self.size)
        self.screen.keypad(True)

    def _refresh(self) -> None:
        lower_corner = (pos + size for pos, size in zip(self.position, self.size))
        self.screen.refresh(0, 0, *self.position, *lower_corner)

    def clear(self) -> None:
        """
        Clear the screen.
        """
        self.screen.clear()
        self._refresh()

    def show_menu(self, sessions: List[str], position: int) -> None:
        """
        Show a menu.
        """
        self.screen.clear()
        self.screen.addstr(0, 0, "Running Sessions:")
        for index, session in enumerate(sessions):
            self.screen.addstr(index + 1, 0, session)
        self.screen.move(position + 1, 0)
        self.screen.chgat(position + 1, 0, -1, curses.A_REVERSE)
        self._refresh()

    def _move_down(self) -> None:
        """
        Move the cursor down.
        """
        cursor_y, cursor_x = self.screen.getyx()
        if cursor_y < self.size[0]:
            self.screen.chgat(cursor_y, 0, -1, curses.A_NORMAL)
            self.screen.move(cursor_y + 1, cursor_x)
            self.screen.chgat(cursor_y + 1, 0, -1, curses.A_REVERSE)

    def _move_up(self) -> None:
        """
        Move the cursor up.
        """
        cursor_y, cursor_x = self.screen.getyx()
        if cursor_y > 0:
            self.screen.chgat(cursor_y, 0, -1, curses.A_NORMAL)
            self.screen.move(cursor_y - 1, cursor_x)
            self.screen.chgat(cursor_y - 1, 0, -1, curses.A_REVERSE)
