import pytest

from src.jmux_presenter import JmuxPresenter
from src.jmux_session import SessionLabel
from src.model import Model
from src.view import View


@pytest.fixture
def mock_view(mocker):
    yield mocker.MagicMock(spec=View)


@pytest.fixture
def mock_model(mocker):
    yield mocker.MagicMock(spec=Model)


@pytest.fixture
def test_labels():
    return [SessionLabel("$1", "session1"), SessionLabel("$2", "session2")]


class TestRunningSessionsMenu:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, test_labels):
        self.model = mock_model
        self.view = mock_view
        self.presenter = JmuxPresenter(self.view, self.model)
        self.labels = test_labels

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


class TestSavedSessionsMenu:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, test_labels):
        self.model = mock_model
        self.view = mock_view
        self.presenter = JmuxPresenter(self.view, self.model)
        self.labels = test_labels

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
