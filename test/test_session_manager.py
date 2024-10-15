import json
from dataclasses import asdict
from pathlib import Path

import pytest

from src.models import JmuxSession
from src.session_manager import SessionManager


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
        self.file = mock_folder / "test.json"
        self.manager = session_manager
        self.current_session = test_jmux_session
        self.manager.multiplexer.get_session.return_value = self.current_session

    def test_given_valid_arguments_returns_none(self):
        self.folder.exists.return_value = True
        assert self.manager.save_current_session() is None

    def test_opens_save_file_in_write_mode(self):
        self.manager.save_current_session()
        self.file.open.assert_called_once_with("w")

    def test_writes_to_save_file(self):
        self.manager.save_current_session()
        self.file.open().write.assert_called()

    def test_writes_json_object_to_save_file(self):
        self.manager.save_current_session()
        written_data = "".join(
            call[0][0] for call in self.file.open().write.call_args_list
        )
        try:
            json.loads(written_data)
            assert True
        except json.JSONDecodeError:
            assert False

    def test_writes_correct_data_to_save_file(self):
        self.manager.save_current_session()
        written_data = "".join(
            call[0][0] for call in self.file.open().write.call_args_list
        )
        assert json.loads(written_data) == asdict(self.current_session)


class TestLoadSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_folder, session_manager, test_jmux_session, mocker):
        self.folder = mock_folder
        self.manager = session_manager
        self.session_file = mock_folder / "test.json"
        self.jmux_session = test_jmux_session
        mocker.patch("json.load", return_value=asdict(self.jmux_session))
        mocker.patch.object(self.manager.multiplexer, "list_sessions", return_value=[])

    def test_given_valid_arguments_returns_instance_of_JmuxSession(self):
        assert isinstance(self.manager.load_session("test"), JmuxSession)

    def test_throws_file_not_found_error_if_session_file_does_not_exist(self):
        self.session_file.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            self.manager.load_session("test")

    def test_throws_value_error_if_session_already_exists(self, mocker):
        mocker.patch.object(
            self.manager.multiplexer, "list_sessions", return_value=[self.jmux_session]
        )
        with pytest.raises(ValueError):
            self.manager.load_session("test")

    def test_opens_session_file_in_read_mode(self):
        self.manager.load_session("test")
        self.session_file.open.assert_called_once_with("r")

    def test_returns_JmuxSession_with_correct_data(self):
        assert self.manager.load_session("test") == self.jmux_session

    def test_given_valid_arguments_builds_session(self, mocker):
        mocker.patch("json.load", return_value=asdict(self.jmux_session))
        self.manager.load_session("test")
        self.manager.multiplexer.create_session.assert_called_once_with(
            self.jmux_session
        )


class TestDeleteSessionFile:
    @pytest.fixture(autouse=True)
    def setup(self, mock_folder, session_manager, mocker):
        self.folder = mock_folder
        self.manager = session_manager
        self.session_file = mock_folder / "test.json"
        mocker.patch.object(self.manager.multiplexer, "list_sessions", return_value=[])

    def test_throws_file_not_found_error_if_session_file_does_not_exist(self):
        self.session_file.exists.return_value = False
        with pytest.raises(FileNotFoundError):
            self.manager.delete_session_file("test")

    def test_returns_none_given_valid_arguments(self):
        assert self.manager.delete_session_file("test") is None

    def test_deletes_session_file(self):
        self.manager.delete_session_file("test")
        self.session_file.unlink.assert_called_once()

    def test_kills_session_if_session_exists(self, mocker, test_jmux_session):
        mocker.patch.object(
            self.manager.multiplexer, "list_sessions", return_value=[test_jmux_session]
        )
        mocker.patch.object(
            self.manager.multiplexer, "get_session", return_value=test_jmux_session
        )
        self.manager.delete_session_file("test")
        self.manager.multiplexer.kill_session.assert_called_once_with(test_jmux_session)
