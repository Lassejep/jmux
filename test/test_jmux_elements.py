import pytest

from src.multiplexer import TmuxAPI
from src.elements import JmuxSession, JmuxWindow, JmuxPane
from src.elements import JmuxLoader, JmuxBuilder


class mock_tmux_api:
    def __init__(self):
        self.sessions = []
        self.windows = []
        self.panes = []
        self.create_session("test_session")
        assert len(self.sessions) == 1

    def is_running(self):
        return True

    def create_session(self, name):
        jmux_session = JmuxSession(name, f"${len(self.sessions)}", [])
        for session in self.sessions:
            if session.id == jmux_session.id:
                raise ValueError("Session already exists")
        self.sessions.append(jmux_session)
        self.create_window("test_window", jmux_session.id)
        return jmux_session.id

    def create_window(self, name, session_id):
        window = JmuxWindow(name, f"@{len(self.windows)}", "tiled", True, [])
        for session in self.sessions:
            if session.id == session_id:
                session.windows.append(window)
                self.windows.append(window)
        self.create_pane(window.id)
        return window.id

    def create_pane(self, window_id):
        pane = JmuxPane(f"%{len(self.panes)}", True, "/tmp")
        for window in self.windows:
            if window.id == window_id:
                window.panes.append(pane)
                self.panes.append(pane)
        return pane.id

    def get(self, keys, target=None):
        if not isinstance(keys, list):
            keys = [keys]
        values = {}
        if len(self.sessions) == 0:
            return values
        data = self._get_data(target)
        if not data:
            return values
        for key in keys:
            values[key] = data[key]
        return values

    def _get_data(self, target):
        if target is None:
            target = self.sessions[-1].id
        if target.startswith("$"):
            return self._get_session_data(target)
        elif target.startswith("@"):
            return self._get_window_data(target)
        elif target.startswith("%"):
            return self._get_pane_data(target)

    def _get_session_data(self, target):
        data = None
        ids = target.split(":")
        for session in self.sessions:
            if session.id != ids[0]:
                continue
            if len(ids) != 1:
                data = self._get_window_data(
                    session.windows[int(ids[1]) - 1].id)
                break
            data = {"session_name": session.name,
                    "session_id": session.id,
                    "windows": len(session.windows)}
        return data

    def _get_window_data(self, target):
        data = None
        ids = target.split(".")
        for window in self.windows:
            if window.id != ids[0]:
                continue
            if len(ids) != 1:
                data = self._get_pane_data(window.panes[int(ids[1]) - 1].id)
                break
            data = {"window_name": window.name,
                    "window_id": window.id,
                    "layout": window.layout,
                    "window_focus": int(window.focus),
                    "panes": len(window.panes)}
        return data

    def _get_pane_data(self, pane_id):
        data = None
        for pane in self.panes:
            if pane.id != pane_id:
                continue
            data = {"pane_id": pane.id,
                    "pane_focus": int(pane.focus),
                    "pane_current_dir": pane.current_dir}
        return data


@pytest.fixture()
def tmux_api(mocker):
    mock_api = mock_tmux_api()
    mocker.patch.object(TmuxAPI, "__new__", return_value=mock_api)
    tmux_api = TmuxAPI()
    yield tmux_api


@pytest.fixture()
def jmux_loader(tmux_api):
    yield JmuxLoader(tmux_api)


@pytest.fixture()
def jmux_builder(tmux_api):
    yield JmuxBuilder(tmux_api)


@pytest.fixture()
def current_session(tmux_api):
    yield tmux_api.get("session_id")["session_id"]


@pytest.fixture()
def current_session_window(tmux_api, current_session):
    yield tmux_api.get("window_id", f"{current_session}:1")["window_id"]


@pytest.fixture()
def current_session_pane(tmux_api, current_session_window):
    yield tmux_api.get("pane_id", f"{current_session_window}.1")["pane_id"]


@pytest.fixture()
def test_jmux_pane():
    yield JmuxPane("test_pane", True, "/tmp")


@pytest.fixture()
def test_jmux_window(test_jmux_pane):
    yield JmuxWindow("test_window", "@10", "tiled", True, [test_jmux_pane])


@pytest.fixture()
def test_jmux_session(test_jmux_window):
    yield JmuxSession("test_session", "$30", [test_jmux_window])


class TestJmuxLoader:
    """Test the JmuxLoader class."""

    def test_throws_exception_given_invalid_multiplexer(self):
        with pytest.raises(ValueError):
            JmuxLoader(None)

    def test_load_returns_type_jmux_session(self, jmux_loader):
        jmux_session = jmux_loader.load()
        assert isinstance(jmux_session, JmuxSession)

    def test_load_throws_exception_if_called_outside_of_a_session(
            self, jmux_loader, mocker):
        mocker.patch.object(jmux_loader.multiplexer, 'is_running',
                            return_value=False)
        with pytest.raises(EnvironmentError):
            jmux_loader.load()

    def test_load_returns_jmux_session_with_current_session_id(
            self, jmux_loader, current_session):
        jmux_session = jmux_loader.load()
        assert jmux_session.id == current_session

    def test_load_returns_jmux_session_with_current_session_name(
            self, jmux_loader, tmux_api):
        jmux_session = jmux_loader.load()
        current_session_name = tmux_api.get("session_name")["session_name"]
        assert jmux_session.name == current_session_name

    def test_load_returns_jmux_session_with_current_windows(
            self, jmux_loader, tmux_api):
        jmux_session = jmux_loader.load()
        current_windows = tmux_api.get("windows")["windows"]
        assert len(jmux_session.windows) == current_windows

    def test_load_returns_jmux_session_with_current_window_name(
            self, jmux_loader, tmux_api, current_session_window):
        jmux_session = jmux_loader.load()
        current_window_name = tmux_api.get(
            "window_name", current_session_window)["window_name"]
        assert jmux_session.windows[0].name == current_window_name

    def test_load_returns_jmux_session_with_current_window_id(
            self, jmux_loader, tmux_api, current_session_window):
        jmux_session = jmux_loader.load()
        current_window_id = tmux_api.get(
            "window_id", current_session_window)["window_id"]
        assert jmux_session.windows[0].id == current_window_id

    def test_load_returns_jmux_session_with_current_window_layout(
            self, jmux_loader, tmux_api, current_session_window):
        jmux_session = jmux_loader.load()
        current_layout = tmux_api.get(
            "layout", current_session_window)["layout"]
        assert jmux_session.windows[0].layout == current_layout

    def test_load_returns_jmux_session_with_current_window_focus(
            self, jmux_loader, tmux_api, current_session_window):
        jmux_session = jmux_loader.load()
        current_focus = tmux_api.get(
            "window_focus", current_session_window)["window_focus"]
        assert jmux_session.windows[0].focus == bool(current_focus)

    def test_load_returns_jmux_session_with_current_panes(
            self, jmux_loader, tmux_api, current_session_window):
        jmux_session = jmux_loader.load()
        current_panes = tmux_api.get(
            "panes", current_session_window)["panes"]
        assert len(jmux_session.windows[0].panes) == current_panes

    def test_load_returns_jmux_session_with_current_pane_id(
            self, jmux_loader, tmux_api, current_session_pane):
        jmux_session = jmux_loader.load()
        current_pane_id = tmux_api.get(
            "pane_id", current_session_pane)["pane_id"]
        assert jmux_session.windows[0].panes[0].id == current_pane_id

    def test_load_returns_jmux_session_with_current_pane_focus(
            self, jmux_loader, tmux_api, current_session_pane):
        jmux_session = jmux_loader.load()
        current_focus = tmux_api.get(
            "pane_focus", current_session_pane)["pane_focus"]
        assert jmux_session.windows[0].panes[0].focus == bool(current_focus)

    def test_load_returns_jmux_session_with_current_pane_current_dir(
            self, jmux_loader, tmux_api, current_session_pane):
        jmux_session = jmux_loader.load()
        current_dir = tmux_api.get(
            "pane_current_dir", current_session_pane)["pane_current_dir"]
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
            self, jmux_builder, tmux_api):
        existing_session_name = tmux_api.get("session_name")["session_name"]
        existing_session_id = tmux_api.get("session_id")["session_id"]
        existing_session = JmuxSession(
            existing_session_name, existing_session_id, [])
        with pytest.raises(ValueError):
            jmux_builder.build(existing_session)

    def test_build_valid_session_returns_none(
            self, jmux_builder, test_jmux_session):
        assert jmux_builder.build(test_jmux_session) is None

    def test_build_creates_a_session(
            self, tmux_api, jmux_builder, test_jmux_session):
        sessions_before = len(tmux_api.sessions)
        jmux_builder.build(test_jmux_session)
        sessions_after = len(tmux_api.sessions)
        assert sessions_after == sessions_before + 1

    def test_build_creates_session_with_correct_name(
            self, tmux_api, jmux_builder, test_jmux_session):
        jmux_builder.build(test_jmux_session)
        session_name = tmux_api.get(
            "session_name", test_jmux_session.id)["session_name"]
        assert test_jmux_session.name == session_name

    def test_build_creates_tmux_window(
            self, tmux_api, jmux_builder, test_jmux_session):
        num_windows_before = len(tmux_api.windows)
        jmux_builder.build(test_jmux_session)
        num_windows_after = len(tmux_api.windows)
        assert num_windows_after == num_windows_before + len(
            test_jmux_session.windows)

    def test_build_creates_tmux_pane(
            self, tmux_api, jmux_builder, test_jmux_session):
        num_panes_before = len(tmux_api.panes)
        jmux_builder.build(test_jmux_session)
        num_panes_after = len(tmux_api.panes)
        expected_panes = sum([len(window.panes)
                              for window in test_jmux_session.windows])
        assert num_panes_after == num_panes_before + expected_panes
