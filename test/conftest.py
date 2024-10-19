from pathlib import Path

import pytest

from src.file_handler import FileHandler
from src.interfaces import Multiplexer
from src.jmux_session import JmuxPane, JmuxSession, JmuxWindow


@pytest.fixture
def mock_multiplexer(mocker):
    yield mocker.Mock(spec=Multiplexer)


@pytest.fixture
def mock_file_handler(mocker):
    yield mocker.Mock(spec=FileHandler)


@pytest.fixture
def mock_folder(mocker):
    mock_path_instance = mocker.MagicMock(spec=Path)
    mocker.patch.object(Path, "__new__", return_value=mock_path_instance)
    mock_path_instance.__truediv__.return_value = Path("/tmp/jmux/test.json")
    mock_path_instance.__str__.return_value = "/tmp/jmux/test.json"
    m_open = mocker.mock_open()
    mock_path_instance.open = m_open
    yield mock_path_instance


@pytest.fixture
def mock_subprocess(mocker):
    subprocess_run = mocker.patch("subprocess.run")

    def set_side_effects(*outputs):
        subprocess_run.side_effect = [mocker.Mock(stdout=output) for output in outputs]

    subprocess_run.set_side_effects = set_side_effects
    return subprocess_run


@pytest.fixture
def jmux_panes():
    pane1 = JmuxPane("%1", True, "/tmp/jmux")
    pane2 = JmuxPane("%2", False, "/tmp/jmux")
    yield pane1, pane2


@pytest.fixture
def jmux_windows(jmux_panes):
    window1 = JmuxWindow("@1", "window1", "test", True, [*jmux_panes])
    window2 = JmuxWindow("@2", "window2", "test", False, [*jmux_panes])
    yield window1, window2


@pytest.fixture
def jmux_session(jmux_windows):
    session = JmuxSession("$1", "session1", [*jmux_windows])
    yield session
