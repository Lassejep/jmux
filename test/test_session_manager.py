import pytest

from src.jmux_session import SessionLabel
from src.session_manager import FileHandler, SessionManager


@pytest.fixture
def mock_file_handler(mocker):
    mock_file_handler = mocker.MagicMock(spec=FileHandler)
    yield mock_file_handler


class TestConstructor:
    def test_given_valid_arguments_returns_instance_of_session_manager(
        self, mock_file_handler, mock_multiplexer
    ):
        assert isinstance(
            SessionManager(mock_file_handler, mock_multiplexer), SessionManager
        )

    def test_with_invalid_file_handler_value_throws_value_error(self, mock_multiplexer):
        with pytest.raises(ValueError):
            SessionManager("test", mock_multiplexer)

    def test_given_invalid_multiplexer_value_throws_value_error(
        self, mock_file_handler
    ):
        with pytest.raises(ValueError):
            SessionManager(mock_file_handler, "test")


class TestSaveCurrentSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_file_handler, mock_multiplexer, test_jmux_session):
        self.file_handler = mock_file_handler
        self.multiplexer = mock_multiplexer
        self.current_session = test_jmux_session
        self.manager = SessionManager(self.file_handler, self.multiplexer)

    def test_returns_none_if_successful(self):
        assert self.manager.save_current_session() is None

    def test_gets_current_session(self):
        self.multiplexer.get_current_session_id.return_value = SessionLabel(
            self.current_session.id, self.current_session.name
        )
        self.manager.save_current_session()
        self.multiplexer.get_session.assert_called_once_with(self.current_session.id)

    def test_saves_current_session_to_file(self):
        self.multiplexer.get_session.return_value = self.current_session
        self.manager.save_current_session()
        self.file_handler.save_session.assert_called_once_with(self.current_session)


class TestLoadSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_file_handler, mock_multiplexer, test_jmux_session, mocker):
        self.file_handler = mock_file_handler
        self.multiplexer = mock_multiplexer
        self.jmux_session = test_jmux_session
        self.manager = SessionManager(self.file_handler, self.multiplexer)
        mocker.patch.object(self.multiplexer, "list_sessions", return_value=[])
        mocker.patch.object(
            self.file_handler, "load_session", return_value=self.jmux_session
        )
        mocker.patch.object(
            self.multiplexer,
            "create_session",
            side_effect=lambda session: setattr(session, "id", "$2"),
        )

    def test_given_valid_arguments_returns_none(self):
        assert self.manager.load_session("test") is None

    def test_throws_value_error_if_session_already_exists(self):
        self.multiplexer.list_sessions.return_value = [
            SessionLabel(self.jmux_session.id, self.jmux_session.name)
        ]
        with pytest.raises(ValueError):
            self.manager.load_session("test")

    def test_loads_session_from_file(self):
        self.manager.load_session("test")
        self.file_handler.load_session.assert_called_once_with("test")

    def test_builds_session_in_multiplexer(self):
        self.manager.load_session("test")
        self.multiplexer.create_session.assert_called_once_with(self.jmux_session)

    def test_saves_session_to_file_with_new_session_ids(self):
        assert self.jmux_session.id == "$1"
        self.manager.load_session("test")
        assert self.jmux_session.id == "$2"
        self.file_handler.save_session.assert_called_once_with(self.jmux_session)


class TestDeleteSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_file_handler, mock_multiplexer, test_jmux_session, mocker):
        self.file_handler = mock_file_handler
        self.multiplexer = mock_multiplexer
        self.jmux_session = test_jmux_session
        self.manager = SessionManager(self.file_handler, self.multiplexer)
        mocker.patch.object(
            self.manager, "_get_session_by_name", return_value=self.jmux_session
        )

    def test_returns_none_given_valid_arguments(self):
        assert self.manager.delete_session("test") is None

    def test_deletes_session_file(self):
        self.manager.delete_session("test")
        self.manager.file_handler.delete_session.assert_called_once_with("test")

    def test_kills_session_if_session_exists(self):
        self.manager.delete_session("test")
        self.manager.multiplexer.kill_session.assert_called_once_with(self.jmux_session)


class TestRenameSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_file_handler, mock_multiplexer, test_jmux_session, mocker):
        self.file_handler = mock_file_handler
        self.multiplexer = mock_multiplexer
        self.jmux_session = test_jmux_session
        self.manager = SessionManager(self.file_handler, self.multiplexer)
        mocker.patch.object(
            self.manager, "_get_session_by_name", return_value=self.jmux_session
        )
        mocker.patch.object(
            self.file_handler, "load_session", side_effect=FileNotFoundError
        )
        mocker.patch.object(
            self.multiplexer,
            "rename_session",
            side_effect=lambda session, new_name: setattr(session, "name", new_name),
        )

    def test_returns_none_given_valid_arguments(self):
        assert self.manager.rename_session("test", "new_name") is None

    def test_saves_file_with_new_name(self):
        self.manager.rename_session("test", "new_name")
        assert self.jmux_session.name == "new_name"
        self.manager.file_handler.save_session.assert_called_once_with(
            self.jmux_session
        )

    def test_throws_value_error_if_file_with_new_name_exists(self, mocker):
        mocker.patch.object(
            self.file_handler, "load_session", return_value=self.jmux_session
        )
        with pytest.raises(ValueError):
            self.manager.rename_session("test", "new_name")

    def test_deletes_file_with_old_name(self):
        self.manager.rename_session("test", "new_name")
        self.manager.file_handler.delete_session.assert_called_once_with("test")

    def test_renames_session_in_multiplexer(self):
        self.manager.rename_session("test", "new_name")
        self.manager.multiplexer.rename_session.assert_called_once_with(
            self.jmux_session, "new_name"
        )
