from pathlib import Path
from dataclasses import asdict
import json

import pytest

from src.session_manager import SessionManager


@pytest.fixture
def session_manager(mock_loader):
    yield SessionManager(mock_loader)


@pytest.fixture
def mock_file(mocker):
    path = Path("/tmp/test")
    mock_path = mocker.MagicMock(spec=path)
    m_open = mocker.mock_open()
    mock_path.open = m_open
    yield mock_path


class TestSessionManagerConstructor:
    def test_throws_exception_if_jmux_loader_is_none(self):
        with pytest.raises(ValueError):
            SessionManager(None)


class TestSaveSessionMethod:
    def test_throws_exception_if_file_path_is_not_pathlib_path(
            self, session_manager):
        with pytest.raises(TypeError):
            session_manager.save_session("test_path")

    def test_creates_file_if_not_exists(
            self, session_manager, mock_file, mock_loader, test_jmux_session):
        mock_file.exists.return_value = False
        mock_file.touch.return_value = None
        mock_loader.load.return_value = test_jmux_session
        session_manager.save_session(mock_file)
        mock_file.touch.assert_called_once()

    def test_gets_current_session_data(
            self, session_manager, mock_file, mock_loader, test_jmux_session):
        mock_loader.load.return_value = test_jmux_session
        session_manager.save_session(mock_file)
        mock_loader.load.assert_called_once()

    def test_writes_current_session_data_to_file(
            self, session_manager, mock_file, mock_loader, test_jmux_session):
        mock_loader.load.return_value = test_jmux_session
        session_manager.save_session(mock_file)
        mock_file.open.assert_called_with("w")

    def test_write_file_data_is_json_format(
            self, session_manager, mock_file, mock_loader, test_jmux_session):
        mock_loader.load.return_value = test_jmux_session
        session_manager.save_session(mock_file)
        written_data = mock_file.open().write.call_args_list
        written_data = ''.join([arg[0][0] for arg in written_data])
        assert written_data == json.dumps(asdict(test_jmux_session), indent=4)
