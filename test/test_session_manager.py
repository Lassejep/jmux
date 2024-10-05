import json
from dataclasses import asdict
from pathlib import Path

import pytest

from src.session_manager import SessionManager


@pytest.fixture
def mock_folder(mocker):
    path = Path("/tmp/jmux/")
    mock_path = mocker.MagicMock(spec=path)
    m_open = mocker.mock_open()
    mock_path.open = m_open
    yield mock_path


@pytest.fixture
def session_manager(mock_folder, mock_multiplexer):
    yield SessionManager(mock_folder, mock_multiplexer)


class TestConstructor:
    def test_given_valid_arguments_returns_instance_of_session_manager(
        self, mock_folder, mock_multiplexer
    ):
        assert isinstance(SessionManager(mock_folder, mock_multiplexer), SessionManager)

    def test_with_invalid_save_folder_value_throws_value_error(self, mock_multiplexer):
        with pytest.raises(ValueError):
            SessionManager("test", mock_multiplexer)

    def test_given_save_folder_does_not_exist_throws_value_error(
        self, mock_folder, mock_multiplexer
    ):
        mock_folder.exists.return_value = False
        with pytest.raises(ValueError):
            SessionManager(mock_folder, mock_multiplexer)

    def test_given_invalid_multiplexer_value_throws_value_error(self, mock_folder):
        with pytest.raises(ValueError):
            SessionManager(mock_folder, "test")


class TestSaveCurrentSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_folder, session_manager, test_jmux_session):
        self.folder = mock_folder
        self.manager = session_manager
        self.current_session = test_jmux_session

    def test_given_valid_arguments_returns_none(self):
        self.folder.exists.return_value = True
        assert self.manager.save_current_session() is None

    def test_nonexistent_save_file_creates_file(self):
        save_file = self.folder / "test.json"
        save_file.exists.return_value = False
        self.manager.save_current_session()
        save_file.touch.assert_called_once()

    def test_opens_save_file_in_write_mode(self):
        save_file = self.folder / "test.json"
        self.manager.save_current_session()
        save_file.open.assert_called_once_with("w")

    def test_writes_json_object_to_save_file(self, mocker):
        save_file = self.folder / "test.json"
        m_open = mocker.mock_open()
        save_file.open = m_open
        self.manager.save_current_session()
