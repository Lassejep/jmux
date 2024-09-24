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
            tmux.get([], "%pane_id")

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
            tmux.create_window("", "$session_id")

    def test_returns_string_given_valid_window_name(self, tmux, shell):
        shell.returns_response("window_id")
        response = tmux.create_window("window_name", "$session_id")
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
            tmux.create_window("window.name", "$session_id")

    def test_throws_exception_given_invalid_target_session(self, tmux, shell):
        shell.returns_response("", stderr="can't find window: invalid_session",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.create_window("window_name", "invalid_session_id")

    def test_creates_new_tmux_window(self, tmux, shell):
        shell.returns_response("window1\nwindow2\n")
        tmux.create_window("window_name", "$session_id")
        command = ["tmux", "list-windows", "-t", "session_name", "-F",
                   "#{window_name}"]
        windows = shell.run(command, capture_output=True).stdout.split("\n")
        assert "window_name" in windows

    def test_returns_id_of_created_window(self, tmux, shell):
        shell.returns_response("window_id")
        assert tmux.create_window("window_name", "$session_id") == "window_id"


class TestCreatePaneMethod:
    """
    Test the create_pane method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_target_window(self, tmux):
        with pytest.raises(ValueError):
            tmux.create_pane("")

    def test_returns_string_given_valid_target_window(self, tmux, shell):
        shell.returns_response("pane_id")
        response = tmux.create_pane("@window_id")
        assert isinstance(response, str)

    def test_returns_id_of_created_pane(self, tmux, shell):
        shell.returns_response("pane_id")
        assert tmux.create_pane("@window_id") == "pane_id"

    def test_throws_exception_given_invalid_target_window(self, tmux, shell):
        shell.returns_response("", stderr="can't find window: invalid_window",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.create_pane("invalid_window_id")

    def test_creates_new_tmux_pane(self, tmux, shell):
        shell.returns_response("pane_id")
        response = tmux.create_pane("@window_id")
        command = ["tmux", "list-panes", "-t", "window_name", "-F",
                   "#{pane_id}"]
        panes = shell.run(command, capture_output=True).stdout.split("\n")
        assert response in panes


class TestFocusElementMethod:
    """
    Test the focus_element method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.focus_element("")

    def test_returns_none_given_valid_target(self, tmux, shell):
        shell.returns_response("")
        assert tmux.focus_element("@target") is None

    def test_throws_exception_given_invalid_target(self, shell, tmux):
        shell.returns_response("", stderr="can't find pane: invalid_target",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.focus_element("invalid_target")

    def test_focuses_on_target(self, tmux, shell):
        shell.returns_response("")
        tmux.focus_element("@target")
        command = ["tmux", "display-message", "-t",
                   "@target", "-p", "#{window_active}"]
        response = shell.run(command, capture_output=True).stdout
        assert response == "1"


class TestKillElementMethod:
    """
    Test the kill_element method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.kill_element("")

    def test_returns_none_given_valid_target(self, tmux, shell):
        shell.returns_response("")
        assert tmux.kill_element("@target") is None

    def test_throws_exception_given_invalid_target(self, tmux, shell):
        shell.returns_response("", stderr="can't find pane: invalid_target",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.kill_element("invalid_target")

    def test_kills_target(self, tmux, shell):
        shell.returns_response("")
        tmux.kill_element("@target")
        command = ["tmux", "list-windows", "-t",
                   "@target", "-F", "#{window_id}"]
        response = shell.run(command, capture_output=True).stdout
        assert len(response.strip()) == 0


class TestChangeWindowLayoutMethod:
    """
    Test the change_window_layout method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_layout(self, tmux, shell):
        shell.returns_response("")
        with pytest.raises(ValueError):
            tmux.change_window_layout("", "@target")

    def test_throws_exception_given_invalid_layout(self, tmux, shell):
        shell.returns_response("", stderr="invalid layout: invalid_layout",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.change_window_layout("invalid_layout", "@target")

    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.change_window_layout("layout", "")

    def test_returns_none_given_valid_layout_and_target(self, tmux, shell):
        shell.returns_response("")
        assert tmux.change_window_layout("layout", "@target") is None

    def test_changes_layout_of_target_window(self, tmux, shell):
        shell.returns_response("")
        tmux.change_window_layout("layout", "@target")
        command = ["tmux", "display-message", "-t",
                   "@target", "-pF", "#{window_layout}"]
        shell.returns_response("layout")
        response = shell.run(command, capture_output=True).stdout
        assert response == "layout"


class TestChangePaneDirectoryMethod:
    """
    Test the change_pane_directory method of the TmuxAPI class.
    """

    def test_throws_exception_given_empty_directory(self, tmux, shell):
        shell.returns_response("")
        with pytest.raises(ValueError):
            tmux.change_pane_directory("", "%target")

    def test_throws_exception_given_invalid_target(self, tmux, shell):
        shell.returns_response("", stderr="can't find pane: invalid_target",
                               returncode=1)
        with pytest.raises(ValueError):
            tmux.change_pane_directory("directory", "%invalid_target")

    def test_throws_exception_given_empty_target(self, tmux):
        with pytest.raises(ValueError):
            tmux.change_pane_directory("directory", "")

    def test_returns_none_given_valid_directory_and_target(self, tmux, shell):
        shell.returns_response("")
        assert tmux.change_pane_directory("directory", "%target") is None

    def test_changes_directory_of_target_pane(self, tmux, shell):
        shell.returns_response("")
        tmux.change_pane_directory("directory", "%target")
        command = ["tmux", "display-message", "-t",
                   "%target", "-pF", "#{pane_current_path}"]
        shell.returns_response("directory")
        response = shell.run(command, capture_output=True).stdout
        assert response == "directory"
