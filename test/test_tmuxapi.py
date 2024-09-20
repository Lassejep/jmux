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

    def test_returns_none_given_valid_session_name(
            self, tmux, shell):
        shell.returns_response("")
        assert tmux.create_session("session_name") is None

    invalid_names = ["session.name", "session:name", "session\tname",
                     "session\nname", " ", "   ", "\t", "\n", "    \t"]

    @pytest.mark.parametrize("name", invalid_names)
    def test_throws_exception_given_invalid_session_name(self, tmux, name):
        with pytest.raises(ValueError):
            tmux.create_session(name)

    def test_creates_new_tmux_session(self, tmux, shell):
        shell.returns_response("session1\nsession2\n")
        tmux.create_session("session_name")
        command = ["tmux", "list-sessions", "-F", "#{session_name}"]
        sessions = shell.run(command, capture_output=True).stdout.split("\n")
        assert "session_name" in sessions


class TestCreateWindowMethod:
    """
    Test the create_window method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_window_name(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_window("", "session_name")

    def test_returns_exception_given_invalid_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "")
