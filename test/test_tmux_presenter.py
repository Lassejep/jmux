import pytest

from src.gui import View
from src.tmux_gui import TmuxPresenter


@pytest.fixture
def mock_session_manager(mocker):
    yield mocker.MagicMock()


@pytest.fixture
def mock_view(mocker):
    view = mocker.MagicMock(spec=View)
    yield view


class TestShowSessionMenu:
    @pytest.fixture(autouse=True)
    def setup(self, mock_session_manager, mock_view, mocker):
        self.manager = mock_session_manager
        self.view = mock_view
        self.presenter = TmuxPresenter(self.view, self.manager)
        mocker.patch.object(self.presenter, "_update_saved_sessions")

    def test_shows_menu(self):
        self.presenter.saved_sessions = ["session1", "session2"]
        self.presenter.show_session_menu()
        self.view.show_menu.assert_called_once_with(
            [(1, 0, "1. session1"), (2, 0, "2. session2")]
        )

    def test_updates_saved_sessions(self):
        self.presenter.show_session_menu()
        self.presenter._update_saved_sessions.assert_called_once()

    def test_shows_menu_with_no_sessions(self):
        self.presenter.saved_sessions = []
        self.presenter.show_session_menu()
        self.view.show_menu.assert_called_once_with([])


class TestHandleInput:
    @pytest.fixture(autouse=True)
    def setup(self, mock_session_manager, mock_view, mocker):
        self.manager = mock_session_manager
        self.view = mock_view
        self.presenter = TmuxPresenter(self.view, self.manager)
        self.presenter.position = 2
        self.presenter.saved_sessions = ["session1", "session2", "session3"]
        mocker.patch.object(self.presenter, "exit_program")

    def test_j_key_calls_cursor_down(self):
        self.presenter.handle_input(ord("j"))
        self.view.cursor_down.assert_called_once()

    def test_j_key_does_not_call_cursor_down_if_position_is_max(self):
        self.presenter.position = 3
        self.presenter.handle_input(ord("j"))
        self.view.cursor_down.assert_not_called()

    def test_k_key_calls_cursor_up(self):
        self.presenter.handle_input(ord("k"))
        self.view.cursor_up.assert_called_once()

    def test_k_key_does_not_call_cursor_up_if_position_is_min(self):
        self.presenter.position = 1
        self.presenter.handle_input(ord("k"))
        self.view.cursor_up.assert_not_called()

    def test_invalid_key_does_not_raise_exception(self):
        assert self.presenter.handle_input("ø") is None

    def test_invalid_key_shows_error_message(self):
        self.presenter.handle_input("ø")
        self.view.show_error.assert_called_once()

    def test_q_key_exits_program(self):
        self.presenter.handle_input(ord("q"))
        self.presenter.exit_program.assert_called_once()

    def test_escape_key_exits_program(self):
        self.presenter.handle_input(27)
        self.presenter.exit_program.assert_called_once()

    def test_enter_key_loads_session(self, mocker):
        mocker.patch.object(self.presenter, "load_session")
        self.presenter.handle_input(10)
        self.presenter.load_session.assert_called_once()


class TestLoadSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_session_manager, mock_view, mocker):
        self.manager = mock_session_manager
        self.view = mock_view
        self.presenter = TmuxPresenter(self.view, self.manager)
        self.presenter.position = 2
        self.presenter.saved_sessions = ["session1", "session2", "session3"]
        mocker.patch.object(self.presenter, "exit_program")

    def test_loads_session(self):
        self.presenter.handle_input(10)
        self.manager.load_session.assert_called_once_with("session2")

    def test_does_not_load_session_if_no_sessions(self):
        self.presenter.saved_sessions = []
        self.presenter.handle_input(10)
        self.manager.load_session.assert_not_called()

    def test_shows_error_message_if_no_sessions(self):
        self.presenter.saved_sessions = []
        self.presenter.handle_input(10)
        self.view.show_error.assert_called_once()

    def test_exits_program_after_loading_session(self):
        self.presenter.handle_input(10)
        self.manager.load_session.assert_called_once()
        self.presenter.exit_program.assert_called_once()


class TestExitProgram:
    @pytest.fixture(autouse=True)
    def setup(self, mock_session_manager, mock_view, mocker):
        self.manager = mock_session_manager
        self.view = mock_view
        self.presenter = TmuxPresenter(self.view, self.manager)
        self.sys_exit = mocker.patch("sys.exit")

    def test_stops_view(self):
        self.presenter.exit_program()
        self.view.stop.assert_called_once()

    def test_exits_program(self):
        self.presenter.exit_program()
        self.sys_exit.assert_called_once_with(0)
