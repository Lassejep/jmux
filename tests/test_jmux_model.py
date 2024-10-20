import pytest

from src.services import JmuxModel


class TestConstructor:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler

    def test_invalid_multiplexer_argument_raises_value_error(self):
        with pytest.raises(ValueError):
            JmuxModel(self.file_handler, self.file_handler)
        with pytest.raises(ValueError):
            JmuxModel(None, self.file_handler)

    def test_invalid_file_handler_argument_raises_value_error(self):
        with pytest.raises(ValueError):
            JmuxModel(self.multiplexer, self.multiplexer)
        with pytest.raises(ValueError):
            JmuxModel(self.multiplexer, None)

    def test_valid_arguments_set_multiplexer_and_file_handler(self):
        model = JmuxModel(self.multiplexer, self.file_handler)
        assert model.multiplexer == self.multiplexer
        assert model.file_handler == self.file_handler

    def test_returns_instance_of_jmux_model(self):
        model = JmuxModel(self.multiplexer, self.file_handler)
        assert isinstance(model, JmuxModel)


class TestCreateSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.model = JmuxModel(self.multiplexer, self.file_handler)

    def test_calls_multiplexer_create_new_session_with_session_name(self):
        self.model.create_session("session1")
        self.multiplexer.create_new_session.assert_called_once_with("session1")


class TestSaveSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)

    def test_gets_session_data_from_multiplexer(self):
        self.model.save_session(self.session_labels[0])
        self.multiplexer.get_session.assert_called_once_with(self.session_labels[0])

    def test_calls_file_handler_save_session_with_session(self, jmux_session):
        self.multiplexer.get_session.return_value = jmux_session
        self.model.save_session(self.session_labels[0])
        self.file_handler.save_session.assert_called_once_with(jmux_session)


class TestLoadSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)

    def test_running_session_is_focused(self):
        self.multiplexer.list_sessions.return_value = self.session_labels
        self.model.load_session(self.session_labels[0])
        self.multiplexer.focus_session.assert_called_once_with(self.session_labels[0])

    def test_loads_session_from_file_if_label_not_in_multiplexer_sessions(
        self, jmux_session
    ):
        self.multiplexer.list_sessions.return_value = []
        self.file_handler.load_session.return_value = jmux_session
        self.model.load_session(self.session_labels[0])
        self.multiplexer.create_session.assert_called_once_with(jmux_session)
        self.file_handler.save_session.assert_called_once_with(jmux_session)


class TestKillSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)
        self.multiplexer.list_sessions.return_value = self.session_labels

    def test_raises_value_error_if_label_not_in_multiplexer_sessions(self):
        self.multiplexer.list_sessions.return_value = []
        with pytest.raises(ValueError):
            self.model.kill_session(self.session_labels[0])

    def test_raises_value_error_if_label_is_current_session(self):
        self.multiplexer.get_current_session_label.return_value = self.session_labels[0]
        with pytest.raises(ValueError):
            self.model.kill_session(self.session_labels[0])

    def test_calls_multiplexer_kill_session_with_label(self):
        self.model.kill_session(self.session_labels[0])
        self.multiplexer.kill_session.assert_called_once_with(self.session_labels[0])


class TestDeleteSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)
        self.file_handler.list_sessions.return_value = self.session_labels

    def test_raises_value_error_if_label_not_in_file_handler_sessions(self):
        self.file_handler.list_sessions.return_value = []
        with pytest.raises(ValueError):
            self.model.delete_session(self.session_labels[0])

    def test_calls_file_handler_delete_session_with_label_name(self):
        self.model.delete_session(self.session_labels[0])
        self.file_handler.delete_session.assert_called_once_with(
            self.session_labels[0].name
        )


class TestRenameSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)
        self.multiplexer.list_sessions.return_value = self.session_labels
        self.file_handler.list_sessions.return_value = self.session_labels

    def test_rename_multiplexer_session_if_running_session(self):
        self.file_handler.list_sessions.return_value = []
        self.model.rename_session(self.session_labels[0], "new_name")
        self.multiplexer.rename_session.assert_called_once_with(
            self.session_labels[0], "new_name"
        )

    def test_loads_session_file_if_saved_session(self):
        self.multiplexer.list_sessions.return_value = []
        self.model.rename_session(self.session_labels[0], "new_name")
        self.file_handler.load_session.assert_called_once_with(
            self.session_labels[0].name
        )

    def test_saves_renamed_session_to_file_if_saved_session(self, jmux_session):
        self.multiplexer.list_sessions.return_value = []
        self.file_handler.load_session.return_value = jmux_session
        self.model.rename_session(self.session_labels[0], "new_name")
        self.file_handler.save_session.assert_called_once_with(jmux_session)

    def test_deletes_old_session_file_if_saved_session(self):
        self.multiplexer.list_sessions.return_value = []
        self.model.rename_session(self.session_labels[0], "new_name")
        self.file_handler.delete_session.assert_called_once_with(
            self.session_labels[0].name
        )

    def test_empty_new_name_raises_value_error(self):
        with pytest.raises(ValueError):
            self.model.rename_session(self.session_labels[0], "")

    def test_whitespace_new_name_raises_value_error(self):
        with pytest.raises(ValueError):
            self.model.rename_session(self.session_labels[0], " ")

    def test_not_running_session_does_not_rename_multiplexer_session(self):
        self.multiplexer.list_sessions.return_value = []
        self.model.rename_session(self.session_labels[0], "new_name")
        self.multiplexer.rename_session.assert_not_called()

    def test_not_saved_session_does_not_load_session_file(self):
        self.file_handler.list_sessions.return_value = []
        self.model.rename_session(self.session_labels[0], "new_name")
        self.file_handler.load_session.assert_not_called()

    def test_running_and_saved_session_renames_multiplexer_session_and_session_file(
        self, jmux_session
    ):
        self.model.rename_session(self.session_labels[0], "new_name")
        self.multiplexer.rename_session.assert_called_once()
        self.file_handler.load_session.assert_called_once()
        self.file_handler.save_session.assert_called_once()
        self.file_handler.delete_session.assert_called_once()


class TestListSavedSessions:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)

    def test_calls_file_handler_list_sessions(self):
        self.model.list_saved_sessions()
        self.file_handler.list_sessions.assert_called_once()

    def test_returns_list_of_session_labels(self):
        self.file_handler.list_sessions.return_value = self.session_labels
        assert self.model.list_saved_sessions() == self.session_labels

    def test_returns_empty_list_if_no_sessions(self):
        self.file_handler.list_sessions.return_value = []
        assert self.model.list_saved_sessions() == []


class TestListRunningSessions:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)

    def test_calls_multiplexer_list_sessions(self):
        self.model.list_running_sessions()
        self.multiplexer.list_sessions.assert_called_once()

    def test_returns_list_of_session_labels(self):
        self.multiplexer.list_sessions.return_value = self.session_labels
        assert self.model.list_running_sessions() == self.session_labels

    def test_returns_empty_list_if_no_sessions(self):
        self.multiplexer.list_sessions.return_value = []
        assert self.model.list_running_sessions() == []


class TestGetActiveSession:
    @pytest.fixture(autouse=True)
    def setup(self, mock_multiplexer, mock_file_handler, session_labels):
        self.multiplexer = mock_multiplexer
        self.file_handler = mock_file_handler
        self.session_labels = session_labels
        self.model = JmuxModel(self.multiplexer, self.file_handler)

    def test_calls_multiplexer_get_current_session_label(self):
        self.model.get_active_session()
        self.multiplexer.get_current_session_label.assert_called_once()

    def test_returns_current_session_label(self):
        self.multiplexer.get_current_session_label.return_value = self.session_labels[0]
        assert self.model.get_active_session() == self.session_labels[0]
