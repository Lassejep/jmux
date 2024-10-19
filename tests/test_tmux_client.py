import os

import pytest

from src.models import JmuxPane, JmuxSession, JmuxWindow, SessionLabel
from src.services import TmuxClient


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
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"
        self.environ = self.mocker.patch.dict(os.environ, clear=True)

    def test_returns_true_if_tmux_is_running(self):
        self.environ["TMUX"] = "/tmp/self.multiplexer-1001/default"
        assert self.multiplexer.is_running()

    def test_returns_false_if_tmux_is_not_running(self):
        self.environ["TMUX"] = ""
        assert not self.multiplexer.is_running()


class TestListSessions:
    @pytest.fixture(autouse=True)
    def setup(self, mock_subprocess, mocker):
        self.subprocess = mock_subprocess
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"

    def test_returns_list(self):
        assert isinstance(self.multiplexer.list_sessions(), list)

    def test_with_one_session_returns_list_with_one_element(self):
        self.subprocess.return_value.stdout = "$1:default"
        assert len(self.multiplexer.list_sessions()) == 1

    def test_with_session_returns_list_with_element_of_type_SessionLabel(self):
        self.subprocess.return_value.stdout = "$1:default"
        assert all(
            [
                isinstance(session, SessionLabel)
                for session in self.multiplexer.list_sessions()
            ]
        )

    def test_with_session_returns_list_with_correct_id_and_name(self):
        self.subprocess.return_value.stdout = "$1:default"
        session = self.multiplexer.list_sessions()[0]
        assert session.id == "$1"
        assert session.name == "default"

    def test_with_no_tmux_session_returns_empty_list(self):
        self.mocker.patch.object(TmuxClient, "is_running", return_value=False)
        assert self.multiplexer.list_sessions() == []

    def test_with_two_sessions_returns_list_with_two_elements(self):
        self.subprocess.return_value.stdout = "$1:default\n$2:session"
        assert len(self.multiplexer.list_sessions()) == 2


class TestGetSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_subprocess, mocker):
        self.subprocess = mock_subprocess
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"

    def test_nonexistent_session_id_raises_ValueError(self):
        self.subprocess.set_side_effects(list_sessions_out(1))
        with pytest.raises(ValueError):
            self.multiplexer.get_session("$5")

    def test_existing_session_id_returns_JmuxSession(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert isinstance(session, JmuxSession)

    def test_existing_session_id_returns_JmuxSession_with_correct_id_and_name(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert session.id == "$1"
        assert session.name == "session1"

    def test_session_with_one_window_returns_JmuxSession_with_one_window(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert len(session.windows) == 1
        assert isinstance(session.windows[0], JmuxWindow)

    def test_session_with_window_returns_JmuxSession_with_correct_window_name(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert session.windows[0].name == "window1"

    def test_session_with_window_returns_JmuxSession_with_correct_window_layout(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert session.windows[0].layout == "tiled"

    def test_session_with_window_returns_JmuxSession_with_correct_window_focus(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert session.windows[0].focus

    def test_session_1window_1pane_returns_JmuxSession_1window_1pane(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert len(session.windows[0].panes) == 1
        assert isinstance(session.windows[0].panes[0], JmuxPane)

    def test_session_1window_1pane_returns_JmuxSession_1window_1pane_with_correct_id(
        self,
    ):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert session.windows[0].panes[0].id == "%1"

    def test_session_1window_1pane_returns_JmuxSession_1window_1pane_with_correct_focus(
        self,
    ):
        self.subprocess.set_side_effects(
            list_sessions_out(1), list_windows_out(1), list_panes_out(1)
        )
        session = self.multiplexer.get_session("$1")
        assert session.windows[0].panes[0].focus

    def test_session_2windows_returns_JmuxSession_with_2windows(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1),
            list_windows_out(2),
            list_panes_out(1),
            list_panes_out(1),
        )
        session = self.multiplexer.get_session("$1")
        assert len(session.windows) == 2

    def test_session_2windows_2panes_returns_JmuxSession_with_2windows_2panes(self):
        self.subprocess.set_side_effects(
            list_sessions_out(1),
            list_windows_out(2),
            list_panes_out(2),
            list_panes_out(2),
        )
        session = self.multiplexer.get_session("$1")
        assert len(session.windows[0].panes) == 2
        assert len(session.windows[1].panes) == 2


class TestCreateSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_subprocess, jmux_session, mocker):
        self.subprocess = mock_subprocess
        self.session = jmux_session
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"
        self.mocker.patch.object(TmuxClient, "is_running", return_value=True)

    def test_session_with_no_windows_throws_ValueError(self):
        with pytest.raises(ValueError):
            self.multiplexer.create_session(
                JmuxSession(self.session.id, self.session.name, [])
            )

    def test_session_creates_tmux_session(self):
        self.multiplexer.create_session(self.session)
        command = [
            "/usr/bin/tmux",
            "new-session",
            "-ds",
            self.session.name,
            "-PF",
            "#{session_id}",
        ]
        expected_call = self.mocker.call(
            command, capture_output=True, text=True, check=True
        )
        call_count = self.subprocess.mock_calls.count(expected_call)
        print(self.subprocess.mock_calls)
        assert call_count == 1

    def test_session_switches_to_created_session(self):
        self.multiplexer.create_session(self.session)
        command = ["/usr/bin/tmux", "switch-client", "-t", self.session.id]
        expected_call = self.mocker.call(command, check=True)
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_creates_session_with_one_window(self):
        self.multiplexer.create_session(self.session)
        command = [
            "/usr/bin/tmux",
            "neww",
            "-t",
            self.session.id,
            "-n",
            self.session.windows[0].name,
            "-PF",
            "#{window_id}",
        ]
        expected_call = self.mocker.call(
            command, capture_output=True, text=True, check=True
        )
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_creates_session_with_one_pane(self):
        self.session.windows = self.session.windows[:1]
        self.multiplexer.create_session(self.session)
        window_id = self.session.windows[0].id
        pane_dir = self.session.windows[0].panes[0].current_dir
        command = [
            "/usr/bin/tmux",
            "splitw",
            "-t",
            window_id,
            "-c",
            pane_dir,
            "-PF",
            "#{pane_id}",
        ]
        expected_call = self.mocker.call(
            command, capture_output=True, text=True, check=True
        )
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_creates_session_with_correct_layout(self):
        self.session.windows = self.session.windows[:1]
        self.multiplexer.create_session(self.session)
        window_id = self.session.windows[0].id
        layout = self.session.windows[0].layout
        command = [
            "/usr/bin/tmux",
            "select-layout",
            "-t",
            window_id,
            layout,
        ]
        expected_call = self.mocker.call(command, check=True)
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_cleans_default_window(self):
        self.multiplexer.create_session(self.session)
        command = [
            "/usr/bin/tmux",
            "kill-window",
            "-t",
            f"{self.session.id}:1",
        ]
        expected_call = self.mocker.call(command, check=True)
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_session_with_one_window_cleans_default_pane(self):
        self.session.windows = self.session.windows[:1]
        self.multiplexer.create_session(self.session)
        command = [
            "/usr/bin/tmux",
            "kill-pane",
            "-t",
            f"{self.session.windows[0].id}.1",
        ]
        expected_call = self.mocker.call(command, check=True)
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1


class TestGetCurrentSessionId:
    @pytest.fixture(autouse=True)
    def setup(self, mock_subprocess, mocker):
        self.subprocess = mock_subprocess
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"
        self.mocker.patch.object(TmuxClient, "is_running", return_value=True)

    def test_raises_ValueError_if_no_session_is_running(self):
        self.mocker.patch.object(TmuxClient, "is_running", return_value=False)
        with pytest.raises(ValueError):
            self.multiplexer.get_current_session_label()

    def test_returns_SessionLabel(self):
        self.subprocess.return_value.stdout = "$1:default"
        assert isinstance(self.multiplexer.get_current_session_label(), SessionLabel)

    def test_returns_SessionLabel_with_correct_id_and_name(self):
        self.subprocess.return_value.stdout = "$1:default"
        session = self.multiplexer.get_current_session_label()
        assert session.id == "$1"
        assert session.name == "default"


class TestKillSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_subprocess, jmux_session, mocker):
        self.subprocess = mock_subprocess
        self.session = jmux_session
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"
        self.mocker.patch.object(
            TmuxClient, "list_sessions", return_value=[SessionLabel("$1", "default")]
        )
        self.mocker.patch.object(
            TmuxClient,
            "get_current_session_label",
            return_value=SessionLabel("$2", "default"),
        )

    def test_raises_ValueError_if_session_id_does_not_exist(self):
        self.mocker.patch.object(TmuxClient, "list_sessions", return_value=[])
        with pytest.raises(ValueError):
            self.multiplexer.kill_session(self.session)

    def test_kills_session(self):
        self.multiplexer.kill_session(self.session)
        command = ["/usr/bin/tmux", "kill-session", "-t", "$1"]
        expected_call = self.mocker.call(command, check=True)
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_raises_ValueError_if_session_is_currently_active(self):
        self.mocker.patch.object(
            TmuxClient,
            "get_current_session_label",
            return_value=SessionLabel("$1", "default"),
        )
        with pytest.raises(ValueError):
            self.multiplexer.kill_session(self.session)


class TestRenameSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_subprocess, jmux_session, mocker):
        self.subprocess = mock_subprocess
        self.session = jmux_session
        self.mocker = mocker
        self.multiplexer = TmuxClient()
        self.multiplexer._bin = "/usr/bin/tmux"
        self.mocker.patch.object(
            TmuxClient, "list_sessions", return_value=[SessionLabel("$1", "default")]
        )

    def test_raises_ValueError_if_session_id_does_not_exist(self):
        self.mocker.patch.object(TmuxClient, "list_sessions", return_value=[])
        with pytest.raises(ValueError):
            self.multiplexer.rename_session(self.session, "new_name")

    def test_renames_session(self):
        self.multiplexer.rename_session(self.session, "new_name")
        command = [
            "/usr/bin/tmux",
            "rename-session",
            "-t",
            "$1",
            "new_name",
        ]
        expected_call = self.mocker.call(command, check=True)
        call_count = self.subprocess.mock_calls.count(expected_call)
        assert call_count == 1

    def test_updates_session_name(self):
        self.multiplexer.rename_session(self.session, "new_name")
        assert self.session.name == "new_name"

    def test_updates_session_name_even_if_session_doesnt_exist(self):
        self.mocker.patch.object(TmuxClient, "list_sessions", return_value=[])
        with pytest.raises(ValueError):
            self.multiplexer.rename_session(self.session, "new_name")
        assert self.session.name == "new_name"
