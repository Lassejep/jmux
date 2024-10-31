import curses

from src.interfaces import Model

from .presenters import CursesPresenter, InputFieldPresenter, MenuPresenter
from .session_handlers import FileSessions, MultiplexerSessions
from .views import CursesView, InputFieldRenderer, MenuRenderer


class CursesGui:
    def __init__(self, model: Model) -> None:
        self.jmux_model = model
        self.running = False

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

    def _create_command_bar(self) -> None:
        position = (self.screen_height - 2, 1)
        size = (1, self.screen_width - 3)
        self.command_bar_view = InputFieldRenderer(position, size)

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
        self._create_command_bar()
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
        self.command_bar = InputFieldPresenter(self.command_bar_view, self.jmux_model)
        self.presenter = CursesPresenter(
            self.main_view,
            self.jmux_model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def _populate_views(self) -> None:
        self.main_view.presenter = self.presenter
        self.multiplexer_view.presenter = self.multiplexer_menu
        self.file_view.presenter = self.file_menu

    def _main_loop(self) -> None:
        self.presenter.activate()
