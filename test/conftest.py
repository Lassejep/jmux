import subprocess

import pytest

from src.tmux_client import TmuxClient
from src.multiplexer import TerminalMultiplexerClient
from src.elements import JmuxLoader, JmuxBuilder
from src.models import JmuxSession, JmuxWindow, JmuxPane


@pytest.fixture()
def shell(mocker):
    mock_shell = mocker.Mock(spec=subprocess)
    yield mock_shell


@pytest.fixture()
def tmux(shell):
    shell.run.return_value = subprocess.CompletedProcess(
        args=["which", "tmux"], returncode=0, stdout="/usr/bin/tmux",
        stderr="")
    yield TmuxClient(shell)


@pytest.fixture
def multiplexer(mocker):
    mock_multiplexer = mocker.Mock(spec=TerminalMultiplexerClient)
    yield mock_multiplexer


@pytest.fixture
def jmux_loader(multiplexer):
    yield JmuxLoader(multiplexer)


@pytest.fixture
def session_data():
    session_data = {"session_name": "test", "session_id": "$1", "windows": 1}
    window_data = {"window_name": "test", "window_id": "@1", "layout": "test",
                   "window_focus": 0, "panes": 1}
    pane_data = {"pane_id": "%1", "pane_focus": 0, "pane_current_dir": "test"}
    yield session_data, window_data, pane_data


@pytest.fixture
def jmux_builder(multiplexer):
    yield JmuxBuilder(multiplexer)


@pytest.fixture
def test_jmux_session():
    session = JmuxSession("test", "$1", [
        JmuxWindow("test", "@1", "test", False, [
            JmuxPane("%1", False, "test")
        ])
    ])
    yield session
