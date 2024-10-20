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

    def test_initializes_position_to_zero(self):
        presenter = JmuxPresenter(self.view, self.model)
        assert presenter.position == 0

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
        self.presenter = JmuxPresenter(self.view, self.model)
        self.labels = session_labels

    def test_updates_view_with_running_sessions(self):
        self.presenter.running_sessions_menu()
        self.view.show_running_sessions.assert_called_once()

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
        self.view.show_running_sessions.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}"]
        )

    def test_adds_note_to_session_name_if_session_is_saved(self):
        self.model.list_running_sessions.return_value = self.labels
        self.model.list_saved_sessions.return_value = [self.labels[1]]
        self.presenter.running_sessions_menu()
        self.view.show_running_sessions.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name} (saved)"]
        )

    def test_adds_star_to_session_name_if_session_is_current(self):
        self.model.list_running_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.presenter.running_sessions_menu()
        self.view.show_running_sessions.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}*"]
        )

    def test_adds_star_and_note_to_session_name_if_session_is_current_and_saved(self):
        self.model.list_running_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.model.list_saved_sessions.return_value = [self.labels[1]]
        self.presenter.running_sessions_menu()
        self.view.show_running_sessions.assert_called_once_with(
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
        self.presenter = JmuxPresenter(self.view, self.model)
        self.labels = session_labels

    def test_updates_view_with_saved_sessions(self):
        self.presenter.saved_sessions_menu()
        self.view.show_saved_sessions.assert_called_once()

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
        self.view.show_saved_sessions.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}"]
        )

    def test_adds_star_to_session_name_if_session_is_current(self):
        self.model.list_saved_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.presenter.saved_sessions_menu()
        self.view.show_saved_sessions.assert_called_once_with(
            [f"1. {self.labels[0].name}", f"2. {self.labels[1].name}*"]
        )

    def test_adds_star_and_note_to_session_name_if_session_is_current_and_running(self):
        self.model.list_saved_sessions.return_value = self.labels
        self.model.get_active_session.return_value = self.labels[1]
        self.model.list_running_sessions.return_value = [self.labels[1]]
        self.presenter.saved_sessions_menu()
        self.view.show_saved_sessions.assert_called_once_with(
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
        self.view.show_running_sessions.assert_called_once()

    def test_previous_state_is_saved_sessions_menu_returns_to_saved_sessions_menu(self):
        self.presenter.state_stack.get.return_value = State.SAVED_SESSIONS_MENU
        self.presenter.create_session()
        self.view.show_saved_sessions.assert_called_once()
