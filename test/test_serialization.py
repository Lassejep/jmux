import pytest

from src.serialization import dict_to_JmuxSession
from src.serialization import dict_to_JmuxWindow
from src.serialization import dict_to_JmuxPane


@pytest.fixture
def pane_data():
    pane_data = {"id": "%1", "focus": 0, "current_dir": "test"}
    yield pane_data


@pytest.fixture
def window_data(pane_data):
    window_data = {"name": "test", "id": "@1", "layout": "test",
                   "focus": 0, "panes": [pane_data]}
    yield window_data


@pytest.fixture
def session_data(window_data):
    session_data = {"name": "test",
                    "id": "$1", "windows": [window_data]}
    yield session_data


class TestDictToJmuxSession:
    def test_dict_to_JmuxSession(self, session_data, test_jmux_session):
        session = dict_to_JmuxSession(session_data)
        assert session == test_jmux_session


class TestDictToJmuxWindow:
    def test_dict_to_JmuxWindow(self, window_data, test_jmux_session):
        window = dict_to_JmuxWindow(window_data)
        assert window == test_jmux_session.windows[0]


class TestDictToJmuxPane:
    def test_dict_to_JmuxPane(self, pane_data, test_jmux_session):
        pane = dict_to_JmuxPane(pane_data)
        assert pane == test_jmux_session.windows[0].panes[0]
