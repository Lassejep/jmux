from subprocess import CompletedProcess
import os

import pytest

from src.tmux_client import TmuxClient


@pytest.fixture()
def tmux(mock_shell):
    mock_shell.run.return_value = CompletedProcess(
        args=["which", "tmux"], returncode=0,
        stdout="/usr/bin/tmux", stderr="")
    yield TmuxClient(mock_shell)


class TestTmuxClientIsRunningMethod:
    def test_returns_true_if_tmux_is_running(self, tmux, mocker):
        mocker.patch.dict(os.environ, {"TMUX": "/tmp/tmux-1001/default"})
        assert tmux.is_running()

    def test_returns_false_if_tmux_is_not_running(self, tmux, mocker):
        mocker.patch.dict(os.environ, {"TMUX": ""})
        assert not tmux.is_running()


class TestTmuxClientGetMethod:
    def test_throws_exception_given_empty_keys(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout=":", stderr="")
        with pytest.raises(ValueError):
            tmux.get([])
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout=":", stderr="")
        with pytest.raises(ValueError):
            tmux.get([], "$1")

    def test_throws_exception_given_invalid_keys(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "display-message", "-p", "#{invalid_key}:"],
            returncode=0, stdout=":", stderr="")
        with pytest.raises(ValueError):
            tmux.get(["invalid_key"])

    def test_returns_dict_given_valid_keys(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="1:/tmp:", stderr="")
        valid_keys = ["pane_id", "pane_current_path"]
        keys = tmux.get(valid_keys)
        assert isinstance(keys, dict)

    def test_returns_dict_with_key_value_pairs_given_valid_keys(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="1:/tmp:", stderr="")
        valid_keys = ["pane_id", "pane_current_path"]
        keys = tmux.get(valid_keys)
        assert len(keys.values()) == len(valid_keys)

    def test_throws_exception_given_a_mix_of_valid_and_invalid_keys(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="1::", stderr="")
        keys = ["pane_id", "invalid_key"]
        with pytest.raises(ValueError, match="invalid_key"):
            tmux.get(keys)

    def test_throws_exception_given_invalid_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=1, stdout="", stderr="\n")
        keys = ["pane_id"]
        with pytest.raises(ValueError):
            tmux.get(keys, "invalid_target")


class TestTmuxClientCreateSessionMethod:
    def test_throws_exceptiong_given_empty_session_name(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="$1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_session("")

    def test_returns_string_given_valid_session_name(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="$1", stderr="")
        response = tmux.create_session("session_name")
        assert isinstance(response, str)

    invalid_session_names = ["session.name", "session:name", "session\tname",
                             "session\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_session_names)
    def test_throws_exception_given_invalid_session_name(
            self, tmux, mock_shell, name):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="$1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_session(name)

    def test_creates_new_tmux_session(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="$1", stderr="")
        tmux.create_session("session_name")
        assert mock_shell.run.call_count == 2

    def test_returns_id_of_created_session(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="$1", stderr="")
        session_id = tmux.create_session("session_name")
        assert session_id == "$1"


class TestTmuxClientCreateWindowMethod:
    def test_throws_exception_given_empty_window_name(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_window("", "$1")

    def test_returns_string_given_valid_window_name(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        response = tmux.create_window("window_name", "$1")
        assert isinstance(response, str)

    def test_throws_exception_given_empty_target_session(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "")

    invalid_window_names = ["window.name", "window:name", "window\tname",
                            "window\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_window_names)
    def test_throws_exception_given_invalid_window_name(
            self, tmux, mock_shell, name):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_window("window.name", "$1")

    def test_throws_exception_given_invalid_target_session(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "invalid_session_id")

    def test_creates_new_tmux_window(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        tmux.create_window("window_name", "$1")
        assert mock_shell.run.call_count == 2

    def test_returns_id_of_created_window(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="@1", stderr="")
        window_id = tmux.create_window("window_name", "$1")
        assert window_id == "@1"


class TestTmuxClientCreatePaneMethod:
    def test_throws_exception_given_empty_target_window(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="%1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_pane("")

    def test_returns_string_given_valid_target_window(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="%1", stderr="")
        response = tmux.create_pane("@1")
        assert isinstance(response, str)

    def test_returns_id_of_created_pane(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="%1", stderr="")
        pane_id = tmux.create_pane("@1")
        assert pane_id == "%1"

    def test_throws_exception_given_invalid_target_window(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="%1", stderr="")
        with pytest.raises(ValueError):
            tmux.create_pane("invalid_window_id")


class TestTmuxClientFocusElementMethod:
    def test_throws_exception_given_empty_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        with pytest.raises(ValueError):
            tmux.focus_element("")

    def test_returns_none_given_valid_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        assert tmux.focus_element("@1") is None

    def test_throws_exception_given_invalid_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=1, stdout="",
            stderr="can't find window invalid_target")
        with pytest.raises(ValueError):
            tmux.focus_element("invalid_target")

    def test_focuses_on_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        tmux.focus_element("@1")
        assert mock_shell.run.call_count == 2


class TestTmuxClientKillElementMethod:
    def test_throws_exception_given_empty_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        with pytest.raises(ValueError):
            tmux.kill_element("")

    def test_returns_none_given_valid_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        assert tmux.kill_element("@1") is None

    def test_throws_exception_given_invalid_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=1, stdout="",
            stderr="can't find window invalid_target")
        with pytest.raises(ValueError):
            tmux.kill_element("invalid_target")

    def test_kills_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        tmux.kill_element("@1")
        assert mock_shell.run.call_count == 2


class TestTmuxClientChangeWindowLayoutMethod:
    def test_throws_exception_given_empty_layout(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        with pytest.raises(ValueError):
            tmux.change_window_layout("", "@1")

    def test_throws_exception_given_invalid_layout(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=1, stdout="",
            stderr="invalid layout")
        with pytest.raises(ValueError):
            tmux.change_window_layout("invalid_layout", "@1")

    def test_throws_exception_given_empty_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        with pytest.raises(ValueError):
            tmux.change_window_layout("tiled", "")

    def test_returns_none_given_valid_layout_and_target(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        assert tmux.change_window_layout("tiled", "@1") is None


class TestTmuxClientChangePaneDirectoryMethod:
    def test_throws_exception_given_empty_directory(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        with pytest.raises(ValueError):
            tmux.change_pane_directory("", "%1")

    def test_throws_exception_given_invalid_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=1, stdout="",
            stderr="can't find pane invalid_target")
        with pytest.raises(ValueError):
            tmux.change_pane_directory("/tmp", "%invalid_target")

    def test_throws_exception_given_empty_target(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        with pytest.raises(ValueError):
            tmux.change_pane_directory("/tmp", "")

    def test_returns_none_given_valid_directory_and_target(
            self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="", stderr="")
        assert tmux.change_pane_directory("/tmp", "%1") is None

    def test_changes_directory_of_target_pane(self, tmux, mock_shell):
        mock_shell.run.return_value = CompletedProcess(
            args=["tmux", "test"], returncode=0, stdout="%1", stderr="")
        tmux.change_pane_directory("/tmp", "%1")
        assert mock_shell.run.call_count == 2
