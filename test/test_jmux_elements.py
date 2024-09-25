import pytest

from src.elements import JmuxSession, JmuxWindow, JmuxPane
from src.elements import JmuxLoader


@pytest.fixture()
def mock_tmux_api(mocker):
    pane = JmuxPane("pane_id", True, "/home/user")
    window = JmuxWindow("test_window", "window_id", "tiled", True, [pane])
    session = JmuxSession("test_session", "session_id", [window])
    mock_tmux = mocker.patch('src.multiplexer.TmuxAPI')
    mock_tmux.is_running.return_value = True
    tmux_data = {"session_name": session.name, "session_id": session.id,
                 "windows": len(session.windows), "window_name": window.name,
                 "window_id": window.id, "layout": window.layout,
                 "window_focus": window.focus, "panes": len(window.panes),
                 "pane_id": pane.id, "pane_focus": pane.focus,
                 "pane_current_dir": pane.current_dir}
    mock_tmux.get.return_value = tmux_data
    mock_tmux.create_session.return_value = session.id
    mock_tmux.create_window.return_value = window.id
    mock_tmux.create_pane.return_value = pane.id
    return mock_tmux


@pytest.fixture()
def tmux_api(mock_tmux_api):
    yield mock_tmux_api


@pytest.fixture()
def jmux_loader(tmux_api):
    yield JmuxLoader(tmux_api)


@pytest.fixture()
def session(tmux_api):
    session_id = tmux_api.create_session("test_session")
    yield session_id


@pytest.fixture()
def window(tmux_api, session):
    window_id = tmux_api.create_window("test_window", session)
    yield window_id


@pytest.fixture()
def pane(tmux_api, window):
    pane_id = tmux_api.create_pane(window)
    yield pane_id


class TestJmuxLoader:
    """Test the JmuxLoader class."""

    def test_throws_exception_given_invalid_multiplexer(self):
        with pytest.raises(ValueError):
            JmuxLoader(None)

    def test_load_returns_jmux_session(self, jmux_loader, session):
        jmux_session = jmux_loader.load()
        assert isinstance(jmux_session, JmuxSession)

    def test_load_throws_exception_if_called_outside_of_a_session(
            self, jmux_loader, mocker):
        mocker.patch.object(jmux_loader.multiplexer, 'is_running',
                            return_value=False)
        with pytest.raises(EnvironmentError):
            jmux_loader.load()

    def test_load_returns_jmux_session_with_current_session_id(
            self, jmux_loader, session):
        jmux_session = jmux_loader.load()
        assert jmux_session.id == session

    def test_load_returns_jmux_session_with_current_session_name(
            self, jmux_loader, session):
        jmux_session = jmux_loader.load()
        assert jmux_session.name == "test_session"

    def test_load_returns_jmux_session_with_current_windows(
            self, jmux_loader, window):
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].id == window

    def test_load_returns_jmux_session_with_current_window_name(
            self, jmux_loader, window):
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].name == "test_window"

    def test_load_returns_jmux_session_with_current_panes(
            self, jmux_loader, pane):
        jmux_session = jmux_loader.load()
        assert jmux_session.windows[0].panes[0].id == pane
