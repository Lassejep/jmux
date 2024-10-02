from pathlib import Path
from dataclasses import asdict
import json

import pytest

from src.session_manager import SessionManager


@pytest.fixture
def session_manager(mock_loader, mock_builder):
    yield SessionManager(mock_loader, mock_builder)


@pytest.fixture
def mock_file(mocker):
    path = Path("/tmp/test")
    mock_path = mocker.MagicMock(spec=path)
    m_open = mocker.mock_open()
    mock_path.open = m_open
    yield mock_path


class TestSessionManagerConstructor:
    def test_throws_exception_if_jmux_loader_is_none(self, mock_builder):
        with pytest.raises(ValueError):
            SessionManager(None, mock_builder)

    def test_throws_exception_if_jmux_loader_is_not_jmux_loader(
            self, mock_builder):
        with pytest.raises(ValueError):
            SessionManager(mock_builder, mock_builder)

    def test_throws_exception_if_jmux_builder_is_none(self, mock_loader):
        with pytest.raises(ValueError):
            SessionManager(mock_loader, None)

    def test_throws_exception_if_jmux_builder_is_not_jmux_builder(
            self, mock_loader):
        with pytest.raises(ValueError):
            SessionManager(mock_loader, mock_loader)


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


class TestLoadSessionMethod:
    def test_throws_exception_if_file_path_is_not_pathlib_path(
            self, session_manager):
        with pytest.raises(TypeError):
            session_manager.load_session("test_path")

    def test_throws_exception_if_file_does_not_exist(
            self, session_manager, mock_file):
        mock_file.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            session_manager.load_session(mock_file)

    def test_opens_correct_file(
            self, session_manager, mock_file, test_jmux_session):
        mock_file.open().read.return_value = json.dumps(
            asdict(test_jmux_session), indent=4)
        session_manager.load_session(mock_file)
        mock_file.open.assert_called_with("r")

    def test_reads_file_data(
            self, session_manager, mock_file, test_jmux_session):
        mock_file.open().read.return_value = json.dumps(
            asdict(test_jmux_session), indent=4)
        session_manager.load_session(mock_file)
        mock_file.open().read.assert_called_once()

    def test_builds_jmux_session_from_file_data(
            self, session_manager, mock_file, test_jmux_session):
        mock_file.open().read.return_value = json.dumps(
            asdict(test_jmux_session), indent=4)
        session_manager.load_session(mock_file)
        session_manager.jmux_builder.build.assert_called_once_with(
            test_jmux_session)
