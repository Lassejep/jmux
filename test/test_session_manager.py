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
def mock_session_file(mocker):
    file = Path("/tmp/jmux/test.json")
    mock_file = mocker.MagicMock(spec=file)
    m_open = mocker.mock_open()
    mock_file.open = m_open
    yield mock_file


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
    def setup(
        self, mock_folder, session_manager, test_jmux_session, mock_session_file, mocker
    ):
        self.folder = mock_folder
        self.file = mock_session_file
        self.manager = session_manager
        self.current_session = test_jmux_session
        mocker.patch.object(SessionManager, "_create_save_file", return_value=self.file)
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
