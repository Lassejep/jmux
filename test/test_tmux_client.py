import os

import pytest

from src.models import JmuxPane, JmuxSession, JmuxWindow, SessionLabel
from src.tmux_client import TmuxClient


@pytest.fixture
def tmux(mocker):
    mocker.patch("src.tmux_client.TmuxClient._get_binary", return_value="/usr/bin/tmux")
    return TmuxClient()


@pytest.fixture
def mock_subprocess(mocker):
    subprocess_run = mocker.patch("subprocess.run")

    def set_side_effects(*outputs):
        subprocess_run.side_effect = [mocker.Mock(stdout=output) for output in outputs]

    subprocess_run.set_side_effects = set_side_effects
    return subprocess_run


@pytest.fixture
def test_pane():
    return JmuxPane(id="%1", focus=True, current_dir="/tmp/jmux/tests")


@pytest.fixture
def test_window(test_pane):
    return JmuxWindow(
        id="@1", name="window1", layout="tiled", focus=True, panes=[test_pane]
    )


@pytest.fixture
def test_session(test_window):
    return JmuxSession(id="$1", name="session1", windows=[test_window])


def list_sessions_out(number_of_sessions):
    return "\n".join([f"${i}:session{i}" for i in range(1, number_of_sessions + 1)])


def list_windows_out(number_of_windows):
    return "\n".join(
        [f"@{i}:window{i}:tiled:{i % 2}" for i in range(1, number_of_windows + 1)]
    )


def list_panes_out(number_of_panes):
    return "\n".join(
        [f"%{i}:{i % 2}:/tmp/jmux/tests" for i in range(1, number_of_panes + 1)]
    )


class TestIsRunning:
    def test_returns_true_if_tmux_is_running(self, tmux, mocker):
        mocker.patch.dict(os.environ, {"TMUX": "/tmp/tmux-1001/default"})
        assert tmux.is_running()

    def test_returns_false_if_tmux_is_not_running(self, tmux, mocker):
        mocker.patch.dict(os.environ, {"TMUX": ""})
        assert not tmux.is_running()


class TestListSessions:
    def test_returns_list(self, tmux):
        assert isinstance(tmux.list_sessions(), list)

    def test_with_one_session_returns_list_with_one_element(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.return_value.stdout = "$1:default"
        assert len(tmux.list_sessions()) == 1

    def test_with_session_returns_list_with_element_of_type_SessionLabel(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.return_value.stdout = "$1:default"
        assert all(
            [isinstance(session, SessionLabel) for session in tmux.list_sessions()]
        )

    def test_with_session_returns_list_with_correct_id_and_name(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.return_value.stdout = "$1:default"
        session = tmux.list_sessions()[0]
        assert session.id == "$1"
        assert session.name == "default"

    def test_with_no_tmux_session_returns_empty_list(self, tmux, mocker):
        mocker.patch.object(TmuxClient, "is_running", return_value=False)
        assert tmux.list_sessions() == []

    def test_with_two_sessions_returns_list_with_two_elements(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.return_value.stdout = "$1:default\n$2:session"
        assert len(tmux.list_sessions()) == 2


class TestGetSession:
    def test_nonexistent_session_id_raises_ValueError(self, tmux, mock_subprocess):
        mock_subprocess.set_side_effects(list_sessions_out(1))
        with pytest.raises(ValueError):
            tmux.get_session("$5")

    def test_existing_session_id_returns_JmuxSession(self, tmux, mock_subprocess):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert isinstance(session, JmuxSession)

    def test_existing_session_id_returns_JmuxSession_with_correct_id_and_name(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert session.id == "$1"
        assert session.name == "session1"

    def test_session_with_one_window_returns_JmuxSession_with_one_window(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert len(session.windows) == 1
        assert isinstance(session.windows[0], JmuxWindow)

    def test_session_with_window_returns_JmuxSession_with_correct_window_name(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert session.windows[0].name == "window1"

    def test_session_with_window_returns_JmuxSession_with_correct_window_layout(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert session.windows[0].layout == "tiled"

    def test_session_with_window_returns_JmuxSession_with_correct_window_focus(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert session.windows[0].focus

    def test_session_1window_1pane_returns_JmuxSession_1window_1pane(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert len(session.windows[0].panes) == 1
        assert isinstance(session.windows[0].panes[0], JmuxPane)

    def test_session_1window_1pane_returns_JmuxSession_1window_1pane_with_correct_id(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert session.windows[0].panes[0].id == "%1"

    def test_session_1window_1pane_returns_JmuxSession_1window_1pane_with_correct_focus(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = tmux.get_session("$1")
        assert session.windows[0].panes[0].focus

    def test_session_2windows_returns_JmuxSession_with_2windows(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1),
            list_windows_out(2),
            list_panes_out(1),
            list_panes_out(1),
        )
        session = tmux.get_session("$1")
        assert len(session.windows) == 2

    def test_session_2windows_2panes_returns_JmuxSession_with_2windows_2panes(
        self, tmux, mock_subprocess
    ):
        mock_subprocess.set_side_effects(
            list_sessions_out(1),
            list_windows_out(2),
            list_panes_out(2),
            list_panes_out(2),
        )
        session = tmux.get_session("$1")
        assert len(session.windows[0].panes) == 2
        assert len(session.windows[1].panes) == 2


class TestCreateSession:
    def test_session_with_no_windows_throws_ValueError(
        self, tmux, mock_subprocess, test_session
    ):
        with pytest.raises(ValueError):
            tmux.create_session(JmuxSession(test_session.id, test_session.name, []))

    def test_session_creates_tmux_session(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        command = [
            "/usr/bin/tmux",
            f"new-session -ds {test_session.name}",
            "-PF",
            "#{session_id}",
        ]
        expected_call = mocker.call(command, capture_output=True, text=True, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_switches_to_created_session(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        command = ["/usr/bin/tmux", f"switch-client -t {test_session.id}"]
        expected_call = mocker.call(command, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_creates_session_with_one_window(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        command = [
            "/usr/bin/tmux",
            f"neww -t {test_session.id} -n {test_session.windows[0].name}",
            "-PF",
            "#{window_id}",
        ]
        expected_call = mocker.call(command, capture_output=True, text=True, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_creates_session_with_one_pane(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        window_id = test_session.windows[0].id
        pane_dir = test_session.windows[0].panes[0].current_dir
        command = [
            "/usr/bin/tmux",
            f"splitw -t {window_id} -c {pane_dir}",
            "-PF",
            "#{pane_id}",
        ]
        expected_call = mocker.call(command, capture_output=True, text=True, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_creates_session_with_correct_layout(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        window_id = test_session.windows[0].id
        layout = test_session.windows[0].layout
        command = ["/usr/bin/tmux", f"select-layout -t {window_id}", layout]
        expected_call = mocker.call(command, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_cleans_default_window(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        command = ["/usr/bin/tmux", f"kill-window -t {test_session.id}.1"]
        expected_call = mocker.call(command, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_cleans_default_pane(
        self, tmux, mock_subprocess, test_session, mocker
    ):
        tmux.create_session(test_session)
        command = ["/usr/bin/tmux", f"kill-pane -t {test_session.windows[0].id}.1"]
        expected_call = mocker.call(command, check=True)
        call_count = mock_subprocess.mock_calls.count(expected_call)
        assert call_count == 1
