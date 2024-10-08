import pytest

from src.models import JmuxPane, JmuxSession, JmuxWindow
from src.multiplexer import Multiplexer


@pytest.fixture
def mock_multiplexer(mocker):
    yield mocker.Mock(spec=Multiplexer)


@pytest.fixture
def session_data():
    session_data = {"session_name": "test", "session_id": "$1", "session_windows": 1}
    window_data = {
        "window_name": "test",
        "window_id": "@1",
        "window_layout": "test",
        "window_active": 1,
        "window_panes": 1,
    }
    pane_data = {"pane_id": "%1", "pane_active": 1, "pane_current_path": "test"}
    yield session_data, window_data, pane_data


@pytest.fixture
def test_jmux_session():
    session = JmuxSession(
        "$1",
        "test",
        [JmuxWindow("@1", "test", "test", True, [JmuxPane("%1", True, "/tmp/jmux")])],
    )
    yield session
