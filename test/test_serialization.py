import pytest

from src.jmux_session import JmuxPane, JmuxSession, JmuxWindow
from src.serialization import (dict_to_JmuxPane, dict_to_JmuxSession,
                               dict_to_JmuxWindow)


@pytest.fixture
def test_jmux_session():
    pane = JmuxPane(id="%1", focus=0, current_dir="test")
    window = JmuxWindow(name="test", id="@1", layout="test", focus=0, panes=[pane])
    session = JmuxSession(name="test", id="$1", windows=[window])
    yield session


@pytest.fixture
def test_pane_data():
    pane_data = {"id": "%1", "focus": 0, "current_dir": "test"}
    yield pane_data


@pytest.fixture
def test_window_data(test_pane_data):
    window_data = {
        "name": "test",
        "id": "@1",
        "layout": "test",
        "focus": 0,
        "panes": [test_pane_data],
    }
    yield window_data


@pytest.fixture
def test_session_data(test_window_data):
    session_data = {"name": "test", "id": "$1", "windows": [test_window_data]}
    yield session_data


class TestDictToJmuxSession:
    def test_dict_to_JmuxSession(self, test_session_data, test_jmux_session):
        session = dict_to_JmuxSession(test_session_data)
        assert session == test_jmux_session


class TestDictToJmuxWindow:
    def test_dict_to_JmuxWindow(self, test_window_data, test_jmux_session):
        window = dict_to_JmuxWindow(test_window_data)
        assert window == test_jmux_session.windows[0]


class TestDictToJmuxPane:
    def test_dict_to_JmuxPane(self, test_pane_data, test_jmux_session):
        pane = dict_to_JmuxPane(test_pane_data)
        assert pane == test_jmux_session.windows[0].panes[0]
