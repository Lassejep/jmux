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

    def test_returns_formatted_sessions(self):
        self.presenter.saved_sessions = ["session1", "session2"]
        assert self.presenter.show_session_menu() == [
            (1, 0, "1. session1"),
            (2, 0, "2. session2"),
        ]

    def test_returns_empty_list_if_no_sessions(self):
        self.presenter.saved_sessions = []
        assert self.presenter.show_session_menu() == []


class TestHandleInput:
    @pytest.fixture(autouse=True)
    def setup(self, mock_session_manager, mock_view, mocker):
        self.manager = mock_session_manager
        self.view = mock_view
        self.presenter = TmuxPresenter(self.view, self.manager)
        self.presenter.position = 2
        self.presenter.saved_sessions = ["session1", "session2", "session3"]
        self.sys_exit = mocker.patch("sys.exit")

    def test_q_key_exits_program(self):
        self.presenter.handle_input(ord("q"))
        self.sys_exit.assert_called_once_with(0)

    def test_escape_key_exits_program(self):
        self.presenter.handle_input(27)
        self.sys_exit.assert_called_once_with(0)

    def test_j_key_calls_cursor_down(self):
        self.presenter.handle_input(ord("j"))
        self.presenter.view.cursor_down.assert_called_once()

    def test_does_not_call_cursor_down_if_position_is_max(self):
        self.presenter.position = 3
        self.presenter.handle_input(ord("j"))
        self.presenter.view.cursor_down.assert_not_called()

    def test_calls_cursor_up_if_k_key_pressed(self):
        self.presenter.handle_input(ord("k"))
        self.presenter.view.cursor_up.assert_called_once()

    def test_does_not_call_cursor_up_if_position_is_min(self):
        self.presenter.position = 1
        self.presenter.handle_input(ord("k"))
        self.presenter.view.cursor_up.assert_not_called()

    def test_does_not_raise_error_if_invalid_key_pressed(self):
        assert self.presenter.handle_input("ø") is None

    def test_shows_error_message_if_invalid_key_pressed(self):
        self.presenter.handle_input("ø")
        self.view.show_error.assert_called_once()

    def test_loads_session_if_enter_key_pressed(self):
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
