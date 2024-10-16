import json
from dataclasses import asdict
from pathlib import Path

import pytest

from src.models import JmuxSession
from src.session_manager import FileHandler


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
def file_handler(mock_folder):
    yield FileHandler(mock_folder)


class TestConstructor:
    def test_invalid_sessions_folder_value_throws_value_error(self):
        with pytest.raises(ValueError):
            FileHandler("test")

    def test_given_sessions_folder_does_not_exist_throws_value_error(self, mock_folder):
        mock_folder.exists.return_value = False
        with pytest.raises(ValueError):
            FileHandler(mock_folder)

    def test_throws_value_error_if_sessions_folder_is_empty_string(self, mock_folder):
        with pytest.raises(ValueError):
            FileHandler("")

    def test_given_valid_arguments_returns_instance_of_file_handler(self, mock_folder):
        assert isinstance(FileHandler(mock_folder), FileHandler)


class TestSaveSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_folder, file_handler, test_jmux_session):
        self.folder = mock_folder
        self.file = mock_folder / "test.json"
        self.file_handler = file_handler
        self.jmux_session = test_jmux_session

    def test_given_valid_arguments_returns_none(self):
        self.folder.exists.return_value = True
        assert self.file_handler.save_session(self.jmux_session) is None

    def test_opens_save_file_in_write_mode(self):
        self.file_handler.save_session(self.jmux_session)
        self.file.open.assert_called_once_with("w")

    def test_writes_to_save_file(self):
        self.file_handler.save_session(self.jmux_session)
        self.file.open().write.assert_called()

    def test_writes_json_object_to_save_file(self):
        self.file_handler.save_session(self.jmux_session)
        written_data = "".join(
            call[0][0] for call in self.file.open().write.call_args_list
        )
        try:
            json.loads(written_data)
            assert True
        except json.JSONDecodeError:
            assert False

    def test_writes_correct_data_to_save_file(self):
        self.file_handler.save_session(self.jmux_session)
        written_data = "".join(
            call[0][0] for call in self.file.open().write.call_args_list
        )
        assert json.loads(written_data) == asdict(self.jmux_session)


class TestLoadSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_folder, file_handler, test_jmux_session, mocker):
        self.folder = mock_folder
        self.file_handler = file_handler
        self.session_file = mock_folder / "test.json"
        self.jmux_session = test_jmux_session
        mocker.patch("json.load", return_value=asdict(self.jmux_session))

    def test_given_valid_arguments_returns_instance_of_JmuxSession(self):
        assert isinstance(self.file_handler.load_session("test"), JmuxSession)

    def test_throws_file_not_found_error_if_session_file_does_not_exist(self):
        self.session_file.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            self.file_handler.load_session("test")

    def test_opens_session_file_in_read_mode(self):
        self.file_handler.load_session("test")
        self.session_file.open.assert_called_once_with("r")

    def test_returns_JmuxSession_with_correct_data(self):
        assert self.file_handler.load_session("test") == self.jmux_session


class TestDeleteSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_folder, file_handler):
        self.folder = mock_folder
        self.file_handler = file_handler
        self.session_file = mock_folder / "test.json"

    def test_throws_file_not_found_error_if_session_file_does_not_exist(self):
        self.session_file.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            self.file_handler.delete_session("test")

    def test_returns_none_given_valid_arguments(self):
        assert self.file_handler.delete_session("test") is None

    def test_deletes_session_file(self):
        self.file_handler.delete_session("test")
        self.session_file.unlink.assert_called_once()
