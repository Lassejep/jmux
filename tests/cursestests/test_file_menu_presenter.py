import pytest

from src.data_models import Event
from src.interfaces import Presenter
from src.tui.presenters import FileMenuPresenter


class TestConstructor:
    def test_given_valid_arguments_returns_instance_of_file_menu_presenter(
        self, mock_view, mock_model
    ):
        assert isinstance(FileMenuPresenter(mock_view, mock_model), FileMenuPresenter)

    def test_implements_presenter_interface(self, mock_view, mock_model):
        assert isinstance(FileMenuPresenter(mock_view, mock_model), Presenter)


class TestToggleActive:
    def test_toggles_active_state(self, mock_view, mock_model):
        presenter = FileMenuPresenter(mock_view, mock_model)
        presenter.active = False
        presenter.toggle_active()
        assert presenter.active is True
        presenter.toggle_active()
        assert presenter.active is False


class TestUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.session_labels = session_labels
        self.presenter = FileMenuPresenter(self.view, self.model)
        self.model.list_saved_sessions.return_value = self.session_labels

    def test_updates_sessions(self):
        self.model.list_saved_sessions.return_value = []
        self.presenter.update_view()
        assert self.presenter.sessions == []

    def test_invalid_cursor_position(self):
        self.presenter.cursor_position = 10
        self.presenter.update_view()
        assert self.presenter.cursor_position == 1
        self.presenter.cursor_position = -1
        self.presenter.update_view()
        assert self.presenter.cursor_position == 0
        self.model.list_saved_sessions.return_value = []
        self.presenter.cursor_position = 0
        self.presenter.update_view()
        assert self.presenter.cursor_position == 0

    def test_annotates_sessions_with_index(self):
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1", "2. session2"], 0, False
        )

    def test_annotates_active_session(self):
        self.model.get_active_session.return_value = self.session_labels[0]
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1*", "2. session2"], 0, False
        )

    def test_annotates_running_session(self):
        self.model.list_running_sessions.return_value = [self.session_labels[1]]
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1", "2. session2 (running)"], 0, False
        )

    def test_annotates_running_and_active_session(self):
        self.model.get_active_session.return_value = self.session_labels[1]
        self.model.list_running_sessions.return_value = [self.session_labels[1]]
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1", "2. session2* (running)"], 0, False
        )

    def test_annotates_no_sessions(self):
        self.model.list_saved_sessions.return_value = []
        self.presenter.update_view()
        self.view.render.assert_called_once_with([], 0, False)

    def test_annotates_running_session_and_different_active_session(self):
        self.model.get_active_session.return_value = self.session_labels[0]
        self.model.list_running_sessions.return_value = [self.session_labels[1]]
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1*", "2. session2 (running)"], 0, False
        )

    def test_passes_cursor_position_to_view(self):
        self.presenter.cursor_position = 1
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1", "2. session2"], 1, False
        )
        self.presenter.cursor_position = 0
        self.presenter.update_view()
        self.view.render.assert_called_with(["1. session1", "2. session2"], 0, False)

    def test_passes_active_state_to_view(self):
        self.presenter.active = True
        self.presenter.update_view()
        self.view.render.assert_called_once_with(
            ["1. session1", "2. session2"], 0, True
        )
        self.presenter.active = False
        self.presenter.update_view()
        self.view.render.assert_called_with(["1. session1", "2. session2"], 0, False)


class TestGetEvent:
    def test_returns_event_from_view(self, mock_view, mock_model):
        presenter = FileMenuPresenter(mock_view, mock_model)
        mock_view.get_event.return_value = Event.NOOP
        assert presenter.get_event() == Event.NOOP
        mock_view.get_event.assert_called_once()


class TestHandleEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, session_labels):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.session_labels = session_labels
        self.presenter = FileMenuPresenter(self.view, self.model)
        self.presenter.sessions = self.session_labels

    def test_move_up_event_decrements_cursor_position(self):
        self.presenter.cursor_position = 1
        self.presenter.handle_event(Event.MOVE_UP)
        assert self.presenter.cursor_position == 0

    def test_move_up_event_does_not_decrement_cursor_position_below_zero(self):
        self.presenter.cursor_position = 0
        self.presenter.handle_event(Event.MOVE_UP)
        assert self.presenter.cursor_position == 0

    def test_move_down_event_increments_cursor_position(self):
        self.presenter.cursor_position = 0
        self.presenter.handle_event(Event.MOVE_DOWN)
        assert self.presenter.cursor_position == 1

    def test_move_down_event_does_not_increment_cursor_position_above_max(self):
        self.presenter.cursor_position = 1
        self.presenter.handle_event(Event.MOVE_DOWN)
        assert self.presenter.cursor_position == 1

    def test_get_session_event_returns_session_label(self):
        self.presenter.cursor_position = 1
        assert self.presenter.handle_event(Event.GET_SESSION) == self.session_labels[1]
        self.presenter.cursor_position = 0
        assert self.presenter.handle_event(Event.GET_SESSION) == self.session_labels[0]

    other_events = [
        event
        for event in Event
        if event not in [Event.MOVE_UP, Event.MOVE_DOWN, Event.GET_SESSION]
    ]

    @pytest.mark.parametrize("event", other_events)
    def test_other_events_return_none(self, event):
        assert self.presenter.handle_event(event) is None
