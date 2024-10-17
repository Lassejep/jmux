import pytest

from src.tmux_gui import TmuxView


@pytest.fixture
def mock_session_manager(mocker):
    return mocker.MagicMock()


@pytest.fixture
def view(mock_session_manager, mocker):
    mocker.patch("src.tmux_gui.curses")
    return TmuxView(mock_session_manager)


@pytest.fixture
def presenter(view):
    return view.presenter


class TestFormatSessions:
    def test_returns_formatted_sessions(self, presenter, mocker):
        mock_get_sessions = mocker.patch.object(presenter, "_get_sessions")
        mock_get_sessions.return_value = ["session1", "session2"]
        assert presenter.format_sessions() == [
            (1, 0, "1. session1"),
            (2, 0, "2. session2"),
        ]

    def test_returns_empty_list_if_no_sessions(self, presenter, mocker):
        mocker.patch.object(presenter, "_get_sessions", return_value=[])
        assert presenter.format_sessions() == []


class TestHandleInput:
    def test_exits_program_if_q_key_pressed(self, presenter, mocker):
        sys_exit = mocker.patch("sys.exit")
        presenter.handle_input(ord("q"))
        sys_exit.assert_called_once_with(0)

    def test_calls_cursor_down_if_j_key_pressed(self, presenter, mocker):
        mocker.patch.object(presenter.view, "cursor_down")
        presenter.handle_input(ord("j"))
        presenter.view.cursor_down.assert_called_once()

    def test_calls_cursor_up_if_k_key_pressed(self, presenter, mocker):
        mocker.patch.object(presenter.view, "cursor_up")
        presenter.handle_input(ord("k"))
        presenter.view.cursor_up.assert_called_once()
