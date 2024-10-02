import pytest

from src.models import JmuxSession, JmuxWindow, JmuxPane
from src.elements import JmuxLoader, JmuxBuilder


class TestJmuxLoader:
    """Test the JmuxLoader class."""

    def test_throws_exception_given_invalid_multiplexer(self):
        with pytest.raises(ValueError):
            JmuxLoader(None)

    def test_load_returns_type_jmux_session(
            self, jmux_loader, multiplexer, session_data):
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert isinstance(jmux_session, JmuxSession)

    def test_load_throws_exception_if_called_outside_of_a_session(
            self, jmux_loader, multiplexer):
        multiplexer.is_running.return_value = False
        with pytest.raises(EnvironmentError):
            jmux_loader.load()

    def test_load_returns_jmux_session_with_current_session_id(
            self, jmux_loader, multiplexer, session_data):
        current_session = "$1"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.id == current_session

    def test_load_returns_jmux_session_with_current_session_name(
            self, jmux_loader, multiplexer, session_data):
        current_session_name = "test"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.name == current_session_name

    def test_load_returns_jmux_session_with_current_windows(
            self, jmux_loader, multiplexer, session_data):
        current_windows = 1
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert len(jmux_session.windows) == current_windows

    def test_load_returns_jmux_session_with_current_window_name(
            self, jmux_loader, multiplexer, session_data):
        current_window_name = "test"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].name == current_window_name

    def test_load_returns_jmux_session_with_current_window_id(
            self, jmux_loader, multiplexer, session_data):
        current_window_id = "@1"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].id == current_window_id

    def test_load_returns_jmux_session_with_current_window_layout(
            self, jmux_loader, multiplexer, session_data):
        current_layout = "test"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].layout == current_layout

    def test_load_returns_jmux_session_with_current_window_focus(
            self, jmux_loader, multiplexer, session_data):
        current_focus = 0
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].focus == bool(current_focus)

    def test_load_returns_jmux_session_with_current_panes(
            self, jmux_loader, multiplexer, session_data):
        current_panes = 1
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert len(jmux_session.windows[0].panes) == current_panes

    def test_load_returns_jmux_session_with_current_pane_id(
            self, jmux_loader, multiplexer, session_data):
        current_pane_id = "%1"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].panes[0].id == current_pane_id

    def test_load_returns_jmux_session_with_current_pane_focus(
            self, jmux_loader, multiplexer, session_data):
        current_focus = 0
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].panes[0].focus == bool(current_focus)

    def test_load_returns_jmux_session_with_current_pane_current_dir(
            self, jmux_loader, multiplexer, session_data):
        current_dir = "test"
        multiplexer.get.side_effect = session_data
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].panes[0].current_dir == current_dir


class TestJmuxBuilder:
    """Test the JmuxBuilder class."""

    def test_throws_exception_given_invalid_multiplexer(self):
        with pytest.raises(ValueError):
            JmuxBuilder(None)

    def test_build_throws_exception_given_invalid_session(self, jmux_builder):
        with pytest.raises(ValueError):
            jmux_builder.build(None)

    def test_build_throws_exception_given_existing_session(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {"session_name": "test"}
        multiplexer.create_session.return_value = "$1"
        with pytest.raises(ValueError):
            jmux_builder.build(test_jmux_session)

    def test_build_valid_session_returns_none(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        assert jmux_builder.build(test_jmux_session) is None

    def test_build_creates_a_session(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.create_session.assert_called_once()

    def test_build_creates_session_with_correct_name(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.create_session.assert_called_with("test")

    def test_build_creates_tmux_window(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.create_window.assert_called_once()

    def test_build_creates_tmux_pane(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.create_pane.assert_called_once()

    def test_build_two_windows(
            self, jmux_builder, multiplexer, test_jmux_session):
        test_jmux_session.windows.append(JmuxWindow(
            "test", "@2", "test", False, [JmuxPane("%2", False, "test")]))
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        assert multiplexer.create_window.call_count == 2

    def test_build_two_panes_in_one_window(
            self, jmux_builder, multiplexer, test_jmux_session):
        test_jmux_session.windows[0].panes.append(JmuxPane(
            "%2", False, "test"))
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        assert multiplexer.create_pane.call_count == 2

    def test_build_two_panes_in_two_windows(
            self, jmux_builder, multiplexer, test_jmux_session):
        test_jmux_session.windows.append(JmuxWindow(
            "test", "@2", "test", False, [
                JmuxPane("%2", False, "test"), JmuxPane("%3", False, "test")
            ]))
        test_jmux_session.windows[0].panes.append(JmuxPane(
            "%2", False, "test"))
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        assert multiplexer.create_pane.call_count == 4
        assert multiplexer.create_window.call_count == 2

    def test_build_creates_tmux_window_with_correct_name(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.create_window.assert_called_with("test", "$1")

    def test_build_creates_tmux_window_with_correct_layout(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.change_window_layout.assert_called_once()

    def test_build_creates_tmux_window_with_correct_focus(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        test_jmux_session.windows[0].focus = False
        jmux_builder.build(test_jmux_session)
        multiplexer.focus_element.assert_not_called()
        test_jmux_session.windows[0].focus = True
        jmux_builder.build(test_jmux_session)
        multiplexer.focus_element.assert_called_once()

    def test_build_creates_tmux_pane_with_correct_focus(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        test_jmux_session.windows[0].panes[0].focus = False
        jmux_builder.build(test_jmux_session)
        multiplexer.focus_element.assert_not_called()
        test_jmux_session.windows[0].panes[0].focus = True
        jmux_builder.build(test_jmux_session)
        multiplexer.focus_element.assert_called_once()

    def test_build_creates_tmux_pane_with_correct_current_dir(
            self, jmux_builder, multiplexer, test_jmux_session):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        jmux_builder.build(test_jmux_session)
        multiplexer.change_pane_directory.assert_called_once()

    def test_build_throws_exception_if_session_window_list_is_empty(
            self, jmux_builder, multiplexer):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        test_jmux_session = JmuxSession("test", "$1", [])
        with pytest.raises(ValueError):
            jmux_builder.build(test_jmux_session)

    def test_build_throws_exception_if_window_pane_list_is_empty(
            self, jmux_builder, multiplexer):
        multiplexer.get.return_value = {}
        multiplexer.create_session.return_value = "$1"
        test_jmux_session = JmuxSession("test", "$1", [
            JmuxWindow("test", "@1", "test", False, [])
        ])
        with pytest.raises(ValueError):
            jmux_builder.build(test_jmux_session)
