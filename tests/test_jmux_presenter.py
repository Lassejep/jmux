from queue import LifoQueue

import pytest

from src.services.jmux_presenter import JmuxPresenter, State


class TestConstructor:
    @pytest.fixture(autouse=True)
    def setup(self, mock_view, mock_model):
        self.view = mock_view
        self.model = mock_model

    def test_given_valid_arguments_returns_instance_of_jmux_presenter(self):
        assert isinstance(JmuxPresenter(self.view, self.model), JmuxPresenter)

    def test_with_invalid_view_value_throws_type_error(self):
        with pytest.raises(TypeError):
            JmuxPresenter(self.model, self.model)
        with pytest.raises(TypeError):
            JmuxPresenter(None, self.model)

    def test_given_invalid_model_value_throws_type_error(self):
        with pytest.raises(TypeError):
            JmuxPresenter(self.view, self.view)
        with pytest.raises(TypeError):
            JmuxPresenter(self.view, None)

    def test_initializes_position_to_negative_one(self):
        presenter = JmuxPresenter(self.view, self.model)
        assert presenter.position == -1

    def test_initializes_state_stack_to_empty_lifo_queue(self):
        presenter = JmuxPresenter(self.view, self.model)
        assert isinstance(presenter.state_stack, LifoQueue)
        assert presenter.state_stack.empty()

    def test_updates_sessions_on_initialization(self):
        JmuxPresenter(self.view, self.model)
        self.model.list_saved_sessions.assert_called_once()
        self.model.list_running_sessions.assert_called_once()
        self.model.get_active_session.assert_called_once()


class TestRunningSessionsMenu:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)

    def test_updates_view_with_running_sessions(self):
        self.presenter.running_sessions_menu()
        self.view.show_menu.assert_called_once()

    def test_updates_running_sessions_from_model(self):
        call_count = self.model.list_running_sessions.call_count
        self.presenter.running_sessions_menu()
        assert self.model.list_running_sessions.call_count == call_count + 1

    def test_updates_saved_sessions_from_model(self):
        call_count = self.model.list_saved_sessions.call_count
        self.presenter.running_sessions_menu()
        assert self.model.list_saved_sessions.call_count == call_count + 1

    def test_updates_current_session_from_model(self):
        call_count = self.model.get_active_session.call_count
        self.presenter.running_sessions_menu()
        assert self.model.get_active_session.call_count == call_count + 1

    def test_annotates_running_session_name(self):
        self.model.list_running_sessions.return_value = self.labels
        self.presenter.running_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}"]
        )

    def test_adds_note_to_session_name_if_session_is_saved(self):
        self.model.list_running_sessions.return_value = self.labels
        self.model.list_saved_sessions.return_value = [self.labels[1]]
        self.presenter.running_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name} (saved)"]
        )

    def test_adds_star_to_session_name_if_session_is_current(self):
        self.model.list_running_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.presenter.running_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}*"]
        )

    def test_adds_star_and_note_to_session_name_if_session_is_current_and_saved(self):
        self.model.list_running_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.model.list_saved_sessions.return_value = [self.labels[1]]
        self.presenter.running_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}* (saved)"]
        )

    def test_sets_state_stack_to_running_sessions_menu(self):
        self.presenter.running_sessions_menu()
        assert self.presenter.state_stack.get() == State.RUNNING_SESSIONS_MENU


class TestSavedSessionsMenu:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)

    def test_updates_view_with_saved_sessions(self):
        self.presenter.saved_sessions_menu()
        self.view.show_menu.assert_called_once()

    def test_updates_running_sessions_from_model(self):
        call_count = self.model.list_running_sessions.call_count
        self.presenter.saved_sessions_menu()
        assert self.model.list_running_sessions.call_count == call_count + 1

    def test_updates_saved_sessions_from_model(self):
        call_count = self.model.list_saved_sessions.call_count
        self.presenter.saved_sessions_menu()
        assert self.model.list_saved_sessions.call_count == call_count + 1

    def test_updates_current_session_from_model(self):
        call_count = self.model.get_active_session.call_count
        self.presenter.saved_sessions_menu()
        assert self.model.get_active_session.call_count == call_count + 1

    def test_annotates_saved_session_name(self):
        self.model.list_saved_sessions.return_value = self.labels
        self.presenter.saved_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}"]
        )

    def test_adds_star_to_session_name_if_session_is_current(self):
        self.model.list_saved_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.presenter.saved_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}*"]
        )

    def test_adds_star_and_note_to_session_name_if_session_is_current_and_running(self):
        self.model.list_saved_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.model.list_running_sessions.return_value = [self.labels[1]]
        self.presenter.saved_sessions_menu()
        self.view.show_menu.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}* (running)"]
        )

    def test_sets_state_stack_to_saved_sessions_menu(self):
        self.presenter.saved_sessions_menu()
        assert self.presenter.state_stack.get() == State.SAVED_SESSIONS_MENU


class TestCreateSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model):
        self.model = mock_model
        self.view = mock_view
        self.mocker = mocker
        self.presenter = JmuxPresenter(self.view, self.model)
        self.view.create_new_session.return_value = "test"
        self.presenter.state_stack = self.mocker.MagicMock()

    def test_adds_create_session_to_state_stack(self):
        self.presenter.create_session()
        expected_call = self.mocker.call(State.CREATE_SESSION)
        count = self.presenter.state_stack.put.mock_calls.count(expected_call)
        assert count == 1

    def test_gets_name_from_view(self):
        self.presenter.create_session()
        self.view.create_new_session.assert_called_once()

    def test_pops_state_stack_after_getting_name_from_view(self):
        self.presenter.create_session()
        assert self.presenter.state_stack.get.call_count >= 1

    def test_creates_session_with_name(self):
        self.presenter.create_session()
        self.model.create_session.assert_called_once_with("test")

    def test_empty_name_does_not_call_model(self):
        self.view.create_new_session.return_value = ""
        self.presenter.create_session()
        self.model.create_session.assert_not_called()

    def test_previous_state_is_running_sessions_menu_returns_to_running_sessions_menu(
        self,
    ):
        self.presenter.state_stack.get.return_value = State.RUNNING_SESSIONS_MENU
        self.presenter.create_session()
        self.view.show_menu.assert_called_once()

    def test_previous_state_is_saved_sessions_menu_returns_to_saved_sessions_menu(self):
        self.presenter.state_stack.get.return_value = State.SAVED_SESSIONS_MENU
        self.presenter.create_session()
        self.view.show_menu.assert_called_once()


class TestSaveSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.mocker = mocker
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)
        self.presenter.state_stack = self.mocker.MagicMock()
        self.presenter.position = 0
        self.presenter.running_sessions = self.labels
        self.view.get_confirmation.return_value = ord("Y")

    def test_shows_error_if_position_is_negative(self):
        self.presenter.position = -1
        self.presenter.save_session()
        self.view.show_error.assert_called_once()

    def test_shows_error_if_position_is_too_high(self):
        self.presenter.position = 3
        self.presenter.save_session()
        self.view.show_error.assert_called_once()

    def test_does_not_show_error_if_position_is_valid(self):
        self.presenter.save_session()
        self.view.show_error.assert_not_called()

    def test_gets_confirmation_from_view(self):
        self.presenter.save_session()
        self.view.get_confirmation.assert_called_once()

    def test_does_not_save_session_if_confirmation_is_no(self):
        self.view.get_confirmation.return_value = ord("n")
        self.presenter.save_session()
        self.model.save_session.assert_not_called()

    def test_saves_session_if_confirmation_is_yes(self):
        self.view.get_confirmation.return_value = ord("Y")
        self.presenter.save_session()
        self.model.save_session.assert_called_once_with(self.labels[0])


class TestLoadSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.mocker = mocker
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)
        self.presenter.state_stack = self.mocker.MagicMock()
        self.presenter.position = 0
        self.presenter.saved_sessions = self.labels
        self.presenter.state_stack.get.return_value = State.SAVED_SESSIONS_MENU

    def test_valid_position_loads_session(self):
        self.presenter.load_session()
        self.model.load_session.assert_called_once_with(self.labels[0])

    def test_invalid_position_does_not_load_session(self):
        self.presenter.position = -1
        self.presenter.load_session()
        self.model.load_session.assert_not_called()

    def test_returns_to_previous_state(self):
        self.mocker.patch.object(self.presenter, "saved_sessions_menu")
        self.mocker.patch.object(self.presenter, "running_sessions_menu")
        self.presenter.state_stack.get.return_value = State.SAVED_SESSIONS_MENU
        self.presenter.load_session()
        self.presenter.saved_sessions_menu.assert_called_once()
        self.presenter.state_stack.get.return_value = State.RUNNING_SESSIONS_MENU
        self.presenter.load_session()
        self.presenter.running_sessions_menu.assert_called_once()


class TestKillSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.mocker = mocker
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)
        self.presenter.state_stack = self.mocker.MagicMock()
        self.presenter.position = 0
        self.presenter.running_sessions = self.labels
        self.view.get_confirmation.return_value = ord("Y")

    def test_negative_position_shows_error(self):
        self.presenter.position = -1
        self.presenter.kill_session()
        self.view.show_error.assert_called_once()

    def test_position_too_high_shows_error(self):
        self.presenter.position = 3
        self.presenter.kill_session()
        self.view.show_error.assert_called_once()

    def test_invalid_position_does_not_kill_session(self):
        self.presenter.position = -1
        self.presenter.kill_session()
        self.model.kill_session.assert_not_called()

    def test_valid_position_kills_session(self):
        self.presenter.kill_session()
        self.model.kill_session.assert_called_once_with(self.labels[0])

    def test_confirmation_no_does_not_kill_session(self):
        self.view.get_confirmation.return_value = ord("n")
        self.presenter.kill_session()
        self.model.kill_session.assert_not_called()


class TestDeleteSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.mocker = mocker
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)
        self.presenter.state_stack = self.mocker.MagicMock()
        self.presenter.position = 0
        self.presenter.saved_sessions = self.labels
        self.view.get_confirmation.return_value = ord("Y")

    def test_negative_position_shows_error(self):
        self.presenter.position = -1
        self.presenter.delete_session()
        self.view.show_error.assert_called_once()

    def test_position_too_high_shows_error(self):
        self.presenter.position = 3
        self.presenter.delete_session()
        self.view.show_error.assert_called_once()

    def test_invalid_position_does_not_delete_session(self):
        self.presenter.position = -1
        self.presenter.delete_session()
        self.model.delete_session.assert_not_called()

    def test_valid_position_deletes_session(self):
        self.presenter.delete_session()
        self.model.delete_session.assert_called_once_with(self.labels[0])

    def test_confirmation_no_does_not_delete_session(self):
        self.view.get_confirmation.return_value = ord("n")
        self.presenter.delete_session()
        self.model.delete_session.assert_not_called()


class TestRenameSession:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.model = mock_model
        self.view = mock_view
        self.mocker = mocker
        self.labels = session_labels
        self.presenter = JmuxPresenter(self.view, self.model)
        self.presenter.state_stack = self.mocker.MagicMock()
        self.presenter.position = 0
        self.presenter.saved_sessions = self.labels
        self.presenter.state_stack.get.return_value = State.SAVED_SESSIONS_MENU
        self.view.rename_session.return_value = "new name"
        self.view.get_confirmation.return_value = ord("Y")

    def test_negative_position_shows_error(self):
        self.presenter.position = -1
        self.presenter.rename_session()
        self.view.show_error.assert_called_once()

    def test_position_too_high_shows_error(self):
        self.presenter.position = 3
        self.presenter.rename_session()
        self.view.show_error.assert_called_once()

    def test_invalid_position_does_not_rename_session(self):
        self.presenter.position = -1
        self.presenter.rename_session()
        self.model.rename_session.assert_not_called()

    def test_valid_position_renames_session(self):
        self.presenter.rename_session()
        self.model.rename_session.assert_called_once_with(self.labels[0], "new name")

    def test_empty_name_does_not_rename_session(self):
        self.view.rename_session.return_value = ""
        self.presenter.rename_session()
        self.model.rename_session.assert_not_called()

    def test_confirmation_no_does_not_rename_session(self):
        self.view.get_confirmation.return_value = ord("n")
        self.presenter.rename_session()
        self.model.rename_session.assert_not_called()
