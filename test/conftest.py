import subprocess

import pytest

from src.multiplexer import TerminalMultiplexerClient
from src.elements import JmuxLoader, JmuxBuilder
from src.models import JmuxSession, JmuxWindow, JmuxPane


@pytest.fixture()
def mock_shell(mocker):
    yield mocker.Mock(spec=subprocess)


@pytest.fixture
def mock_multiplexer(mocker):
    yield mocker.Mock(spec=TerminalMultiplexerClient)


@pytest.fixture
def mock_loader(mock_multiplexer, mocker):
    jmux_loader = JmuxLoader(mock_multiplexer)
    yield mocker.Mock(spec=jmux_loader)


@pytest.fixture
def mock_builder(mock_multiplexer, mocker):
    jmux_builder = JmuxBuilder(mock_multiplexer)
    yield mocker.Mock(spec=jmux_builder)


@pytest.fixture
def session_data():
    session_data = {"session_name": "test",
                    "session_id": "$1", "session_windows": 1}
    window_data = {"window_name": "test", "window_id": "@1",
                   "window_layout": "test", "window_active": 0,
                   "window_panes": 1}
    pane_data = {"pane_id": "%1", "pane_active": 0,
                 "pane_current_path": "test"}
    yield session_data, window_data, pane_data


@pytest.fixture
def test_jmux_session():
    session = JmuxSession("test", "$1", [
        JmuxWindow("test", "@1", "test", False, [
            JmuxPane("%1", False, "test")
        ])
    ])
    yield session
