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


@pytest.fixture
def presenter(mock_view, mock_session_manager):
    presenter = TmuxPresenter(mock_view, mock_session_manager)
    yield presenter


class TestFormatSessions:
    @pytest.fixture(autouse=True)
    def setup(self, presenter):
        self.presenter = presenter

    def test_returns_formatted_sessions(self, mocker):
        mock_get_sessions = mocker.patch.object(self.presenter, "_get_sessions")
        mock_get_sessions.return_value = ["session1", "session2"]
        assert self.presenter.format_sessions() == [
            (1, 0, "1. session1"),
            (2, 0, "2. session2"),
        ]

    def test_returns_empty_list_if_no_sessions(self, mocker):
        mocker.patch.object(self.presenter, "_get_sessions", return_value=[])
        assert self.presenter.format_sessions() == []


class TestHandleInput:
    @pytest.fixture(autouse=True)
    def setup(self, presenter):
        self.presenter = presenter

    def test_exits_program_if_q_key_pressed(self, mocker):
        sys_exit = mocker.patch("sys.exit")
        self.presenter.handle_input(ord("q"))
        sys_exit.assert_called_once_with(0)

    def test_calls_cursor_down_if_j_key_pressed(self):
        self.presenter.handle_input(ord("j"))
        self.presenter.view.cursor_down.assert_called_once()

    def test_calls_cursor_up_if_k_key_pressed(self):
        self.presenter.handle_input(ord("k"))
        self.presenter.view.cursor_up.assert_called_once()
