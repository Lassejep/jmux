import pytest
import subprocess
import os
from time import sleep

from src.multiplexer import TmuxAPI


@pytest.fixture(scope="class")
def shell():
    yield subprocess


@pytest.fixture(scope="class")
def tmux(shell):
    yield TmuxAPI(shell)


@pytest.fixture(scope="function", autouse=True)
def cleanup(shell):
    yield
    shell.run(["tmux", "kill-session", "-t", "session_name"])


@pytest.fixture(scope="function")
def session_id(shell):
    session_id = shell.run(["tmux", "new-session", "-ds",
                            "session_name", "-PF",
                            "#{session_id}"], capture_output=True,
                           text=True).stdout.strip()
    yield session_id


@pytest.fixture(scope="function")
def window_id(shell, session_id):
    window_id = shell.run(["tmux", "new-window", "-t",
                          session_id, "-n", "window_name", "-PF",
                          "#{window_id}"], capture_output=True,
                          text=True).stdout.strip()
    yield window_id


@pytest.fixture(scope="function")
def pane_id(shell, window_id):
    pane_id = shell.run(["tmux", "split-window", "-t",
                        window_id, "-PF", "#{pane_id}"],
                        capture_output=True, text=True).stdout.strip()
    yield pane_id


@pytest.fixture(scope="function")
def layout():
    yield "tiled"


class TestTmuxAPIIsRunningMethod:
    def test_returns_true_if_tmux_is_running(self, tmux, mocker):
        mocker.patch.dict(os.environ, {"TMUX": "/tmp/tmux-1001/default"})
        assert tmux.is_running()

    def test_returns_false_if_tmux_is_not_running(self, tmux, mocker):
        mocker.patch.dict(os.environ, {"TMUX": ""})
        assert not tmux.is_running()


class TestTmuxAPIGetMethod:
    def test_throws_exception_given_empty_keys(self, tmux):
        with pytest.raises(ValueError):
            tmux.get([])
        with pytest.raises(ValueError):
            tmux.get([], "$1")

    def test_throws_exception_given_invalid_keys(self, tmux):
        with pytest.raises(ValueError):
            tmux.get(["invalid_key"])

    def test_returns_dict_given_valid_keys(self, tmux):
        valid_keys = ["pane_id", "pane_current_path"]
        keys = tmux.get(valid_keys)
        assert isinstance(keys, dict)

    def test_returns_dict_with_key_value_pairs_given_valid_keys(self, tmux):
        valid_keys = ["pane_id", "pane_current_path"]
        keys = tmux.get(valid_keys)
        assert len(keys.values()) == len(valid_keys)

    def test_throws_exception_given_a_mix_of_valid_and_invalid_keys(
            self, tmux):
        keys = ["pane_id", "invalid_key"]
        with pytest.raises(ValueError, match="invalid_key"):
            tmux.get(keys)

    def test_throws_exception_given_invalid_target(self, tmux):
        keys = ["pane_id"]
        with pytest.raises(ValueError):
            tmux.get(keys, "invalid_target")


class TestTmuxAPICreateSessionMethod:
    def test_throws_exceptiong_given_empty_session_name(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_session("")

    def test_returns_string_given_valid_session_name(self, tmux):
        response = tmux.create_session("session_name")
        assert isinstance(response, str)

    invalid_session_names = ["session.name", "session:name", "session\tname",
                             "session\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_session_names)
    def test_throws_exception_given_invalid_session_name(self, tmux, name):
        with pytest.raises(ValueError):
            tmux.create_session(name)

    def test_creates_new_tmux_session(self, tmux, shell):
        tmux.create_session("session_name")
        command = ["tmux", "list-sessions", "-F", "#{session_name}"]
        sessions = shell.run(command, capture_output=True,
                             text=True).stdout.split("\n")
        assert "session_name" in sessions

    def test_returns_id_of_created_session(self, tmux):
        session_id = tmux.create_session("session_name")
        command = ["tmux", "list-sessions", "-F",
                   "#{session_name}:#{session_id}"]
        sessions = tmux.shell.run(command, capture_output=True,
                                  text=True).stdout.split("\n")
        for session in sessions:
            if session.startswith("session_name:"):
                expected_id = session.split(":")[1]
                break
        assert session_id == expected_id


class TestTmuxAPICreateWindowMethod:
    def test_throws_exception_given_empty_window_name(self, tmux, session_id):
        with pytest.raises(ValueError):
            tmux.create_window("", session_id)

    def test_returns_string_given_valid_window_name(self, tmux, session_id):
        response = tmux.create_window("window_name", session_id)
        assert isinstance(response, str)

    def test_throws_exception_given_empty_target_session(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "")

    invalid_window_names = ["window.name", "window:name", "window\tname",
                            "window\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_window_names)
    def test_throws_exception_given_invalid_window_name(self, tmux, name,
                                                        session_id):
        with pytest.raises(ValueError):
            tmux.create_window("window.name", session_id)

    def test_throws_exception_given_invalid_target_session(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "invalid_session_id")

    def test_creates_new_tmux_window(self, tmux, shell, session_id):
        tmux.create_window("window_name", session_id)
        command = ["tmux", "list-windows", "-t", session_id, "-F",
                   "#{window_name}"]
        windows = shell.run(command, capture_output=True,
                            text=True).stdout.split("\n")
        assert "window_name" in windows

    def test_returns_id_of_created_window(self, tmux, session_id):
        window_id = tmux.create_window("window_name", session_id)
        command = ["tmux", "list-windows", "-t", session_id, "-F",
                   "#{window_name}:#{window_id}"]
        windows = tmux.shell.run(command, capture_output=True,
                                 text=True).stdout.split("\n")
        print(windows)
        for window in windows:
            if window.startswith("window_name:"):
                expected_id = window.split(":")[1]
                break
        assert window_id == expected_id


class TestTmuxAPICreatePaneMethod:
    def test_throws_exception_given_empty_target_window(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_pane("")

    def test_returns_string_given_valid_target_window(self, tmux, window_id):
        response = tmux.create_pane(window_id)
        assert isinstance(response, str)

    def test_returns_id_of_created_pane(self, tmux, window_id):
        pane_id = tmux.create_pane(window_id)
        command = ["tmux", "list-panes", "-t", window_id, "-F",
                   "#{pane_id}"]
        panes = tmux.shell.run(command, capture_output=True,
                               text=True).stdout.split("\n")
        assert pane_id in panes

    def test_throws_exception_given_invalid_target_window(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_pane("invalid_window_id")


class TestTmuxAPIFocusElementMethod:
    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.focus_element("")

    def test_returns_none_given_valid_target(self, tmux, window_id):
        assert tmux.focus_element(window_id) is None

    def test_throws_exception_given_invalid_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.focus_element("invalid_target")

    def test_focuses_on_target(self, tmux, shell, window_id):
        tmux.focus_element(window_id)
        command = ["tmux", "display-message", "-t",
                   window_id, "-p", "#{window_active}"]
        response = shell.run(command, capture_output=True,
                             text=True).stdout.strip()
        assert response == "1"


class TestTmuxAPIKillElementMethod:
    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.kill_element("")

    def test_returns_none_given_valid_target(self, tmux, window_id):
        assert tmux.kill_element(window_id) is None

    def test_throws_exception_given_invalid_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.kill_element("invalid_target")

    def test_kills_target(self, tmux, shell, window_id):
        tmux.kill_element(window_id)
        command = ["tmux", "list-windows", "-t",
                   window_id, "-F", "#{window_id}"]
        response = shell.run(command, capture_output=True, text=True).stdout
        assert len(response.strip()) == 0


class TestTmuxAPIChangeWindowLayoutMethod:
    def test_throws_exception_given_empty_layout(self, tmux, window_id):
        with pytest.raises(ValueError):
            tmux.change_window_layout("", window_id)

    def test_throws_exception_given_invalid_layout(self, tmux, window_id):
        with pytest.raises(ValueError):
            tmux.change_window_layout("invalid_layout", window_id)

    def test_throws_exception_given_empty_target(self, tmux, layout):
        with pytest.raises(ValueError):
            tmux.change_window_layout(layout, "")

    def test_returns_none_given_valid_layout_and_target(
            self, tmux, window_id, layout):
        assert tmux.change_window_layout(layout, window_id) is None


class TestTmuxAPIChangePaneDirectoryMethod:
    def test_throws_exception_given_empty_directory(self, tmux, pane_id):
        with pytest.raises(ValueError):
            tmux.change_pane_directory("", pane_id)

    def test_throws_exception_given_invalid_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.change_pane_directory("/tmp", "%invalid_target")

    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.change_pane_directory("/tmp", "")

    def test_returns_none_given_valid_directory_and_target(
            self, tmux, pane_id):
        assert tmux.change_pane_directory("/tmp", pane_id) is None

    @pytest.mark.skip(reason="Test runs slowly")
    def test_changes_directory_of_target_pane(self, tmux, shell, pane_id):
        tmux.change_pane_directory("/tmp", pane_id)
        command = ["tmux", "display-message", "-t",
                   pane_id, "-pF", "#{pane_current_path}"]
        sleep(1)
        response = shell.run(command, capture_output=True,
                             text=True).stdout.strip()
        assert response == "/tmp"
