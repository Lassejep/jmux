import pytest

from test.test_doubles import SubprocessTestDouble
from src.tmuxapi import TmuxAPI


@pytest.fixture(scope="class")
def shell():
    yield SubprocessTestDouble()


@pytest.fixture(scope="class")
def tmux(shell):
    yield TmuxAPI(shell)


class TestGetMethod:
    """
    Test the get method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_keys(self, tmux):
        with pytest.raises(ValueError):
            tmux.get([])
        with pytest.raises(ValueError):
            tmux.get([], "target")

    def test_throws_exception_given_invalid_keys(self, tmux, shell):
        shell.returns_response("")
        with pytest.raises(ValueError):
            tmux.get(["invalid_key"])

    def test_returns_dict_given_valid_keys(self, tmux, shell):
        shell.returns_response("value")
        keys = tmux.get(["valid_key"])
        assert isinstance(keys, dict)

    def test_returns_dict_with_key_value_pair_given_valid_keys(
            self, tmux, shell):
        shell.returns_response("value")
        keys = tmux.get(["valid_key"])
        expected_result = {"valid_key": "value"}
        assert keys == expected_result

    def test_returns_dict_with_multiple_key_value_pairs_given_valid_keys(
            self, tmux, shell):
        shell.returns_response("value1:value2")
        keys = tmux.get(["key1", "key2"])
        expected_result = {"key1": "value1", "key2": "value2"}
        assert keys == expected_result

    def test_throws_exception_given_a_mix_of_valid_and_invalid_keys(
            self, tmux, shell):
        shell.returns_response("value::")
        with pytest.raises(ValueError, match="invalid_key"):
            tmux.get(["valid_key", "invalid_key"])

    def test_throws_exception_given_invalid_target(self, tmux, shell):
        shell.returns_response("")
        with pytest.raises(ValueError):
            tmux.get(["valid_key"], "invalid_target")


class TestCreateSessionMethod:
    """
    Test the create_session method of the TmuxAPI class.
    """

    def test_throws_exceptiong_given_empty_session_name(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_session("")

    def test_returns_string_given_valid_session_name(self, tmux, shell):
        shell.returns_response("session_id")
        response = tmux.create_session("session_name")
        assert isinstance(response, str)

    invalid_session_names = ["session.name", "session:name", "session\tname",
                             "session\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_session_names)
    def test_throws_exception_given_invalid_session_name(self, tmux, name):
        with pytest.raises(ValueError):
            tmux.create_session(name)

    def test_creates_new_tmux_session(self, tmux, shell):
        shell.returns_response("session_id")
        tmux.create_session("session_name")
        command = ["tmux", "list-sessions", "-F", "#{session_name}"]
        sessions = shell.run(command, capture_output=True).stdout.split("\n")
        assert "session_name" in sessions

    def test_returns_id_of_created_session(self, tmux, shell):
        shell.returns_response("session_id")
        assert tmux.create_session("session_name") == "session_id"


class TestCreateWindowMethod:
    """
    Test the create_window method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_window_name(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_window("", "session_name")

    def test_returns_string_given_valid_window_name(self, tmux, shell):
        shell.returns_response("window_id")
        response = tmux.create_window("window_name", "session_name")
        assert isinstance(response, str)

    def test_throws_exception_given_empty_target_session(self, tmux, shell):
        shell.returns_response("")
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "")

    invalid_window_names = ["window.name", "window:name", "window\tname",
                            "window\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_window_names)
    def test_throws_exception_given_invalid_window_name(self, tmux, name):
        with pytest.raises(ValueError):
            tmux.create_window("window.name", "session_name")

    def test_throws_exception_given_invalid_target_session(self, tmux, shell):
        shell.returns_response("", stderr="can't find window: invalid_session",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "invalid_session")

    def test_creates_new_tmux_window(self, tmux, shell):
        shell.returns_response("window1\nwindow2\n")
        tmux.create_window("window_name", "session_name")
        command = ["tmux", "list-windows", "-t", "session_name", "-F",
                   "#{window_name}"]
        windows = shell.run(command, capture_output=True).stdout.split("\n")
        assert "window_name" in windows

    def test_returns_id_of_created_window(self, tmux, shell):
        shell.returns_response("window_id")
        assert tmux.create_window("window_name", "session_name") == "window_id"


class TestCreatePaneMethod:
    """
    Test the create_pane method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_target_window(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_pane("")

    def test_returns_string_given_valid_target_window(self, tmux, shell):
        shell.returns_response("pane_id")
        response = tmux.create_pane("window_name")
        assert isinstance(response, str)

    def test_returns_id_of_created_pane(self, tmux, shell):
        shell.returns_response("pane_id")
        assert tmux.create_pane("window_name") == "pane_id"

    def test_throws_exception_given_invalid_target_window(self, tmux, shell):
        shell.returns_response("", stderr="can't find window: invalid_window",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.create_pane("invalid_window")

    def test_creates_new_tmux_pane(self, tmux, shell):
        shell.returns_response("pane_id")
        response = tmux.create_pane("window_name")
        command = ["tmux", "list-panes", "-t", "window_name", "-F",
                   "#{pane_id}"]
        panes = shell.run(command, capture_output=True).stdout.split("\n")
        assert response in panes
