import curses

from src.interfaces import Model

from .curses_state_machine import CursesStateMachine
from .presenters import CommandBarPresenter, CursesPresenter, MenuPresenter
from .session_handlers import FileSessions, MultiplexerSessions
from .views import CommandBarRenderer, CursesView, MenuRenderer


class CursesGui:
    def __init__(self, model: Model) -> None:
        self.jmux_model = model
        self.running = False
        self.state = CursesStateMachine()

    def run(self) -> None:
        self.running = True
        curses.wrapper(self._setup)

    def _setup(self, stdscr: curses.window) -> None:
        self.screen_height, self.screen_width = stdscr.getmaxyx()
        self._setup_curses()
        self._setup_colors()
        self._create_views(stdscr)
        self._create_presenters()
        self._populate_views()
        self._main_loop()

    def _setup_curses(self) -> None:
        curses.curs_set(0)
        curses.set_escdelay(10)
        curses.noecho()
        curses.cbreak()

    def _setup_colors(self) -> None:
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)

    def _create_message_window(self) -> None:
        position = (self.screen_height - 2, 1)
        size = (1, self.screen_width - 2)
        self.message_window = CommandBarRenderer(position, size)

    def _create_multiplexer_view(self) -> None:
        position = (1, 1)
        size = (self.screen_height - 4, self.screen_width // 2 - 2)
        self.multiplexer_view = MenuRenderer(position, size, "Running Sessions:")

    def _create_file_view(self) -> None:
        position = (1, self.screen_width // 2 + 1)
        size = (self.screen_height - 4, self.screen_width // 2 - 2)
        self.file_view = MenuRenderer(position, size, "Saved Sessions:")

    def _create_views(self, stdscr) -> None:
        self.main_view = CursesView(stdscr)
        self._create_message_window()
        self._create_multiplexer_view()
        self._create_file_view()

    def _create_presenters(self) -> None:
        self.multiplexer_menu = MenuPresenter(
            self.multiplexer_view,
            self.jmux_model,
            MultiplexerSessions(self.jmux_model),
        )
        self.file_menu = MenuPresenter(
            self.file_view, self.jmux_model, FileSessions(self.jmux_model)
        )
        self.message_menu = CommandBarPresenter(self.message_window, self.jmux_model)
        self.presenter = CursesPresenter(
            self.main_view,
            self.jmux_model,
            self.state,
            self.multiplexer_menu,
            self.file_menu,
            self.message_menu,
        )

    def _populate_views(self) -> None:
        self.main_view.presenter = self.presenter
        self.multiplexer_view.presenter = self.multiplexer_menu
        self.file_view.presenter = self.file_menu
        self.message_window.presenter = self.message_menu

    def _main_loop(self) -> None:
        self.presenter.activate()
