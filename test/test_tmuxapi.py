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

    def test_returns_dict_with_key_value_pair_given_valid_keys(self, tmux, shell):
        shell.returns_response("value")
        keys = tmux.get(["valid_key"])
        expected_result = {"valid_key": "value"}
        assert keys == expected_result

    def test_returns_dict_with_multiple_key_value_pairs_given_valid_keys(self, tmux, shell):
        shell.returns_response("value1:value2")
        keys = tmux.get(["key1", "key2"])
        expected_result = {"key1": "value1", "key2": "value2"}
        assert keys == expected_result

    def test_throws_exception_given_a_mix_of_valid_and_invalid_keys(self, tmux, shell):
        shell.returns_response("value::")
        with pytest.raises(ValueError, match="invalid_key"):
            tmux.get(["valid_key", "invalid_key"])

    def test_throws_exception_given_invalid_target(self, tmux, shell):
        shell.returns_response("")
        with pytest.raises(ValueError):
            tmux.get(["valid_key"], "invalid_target")
