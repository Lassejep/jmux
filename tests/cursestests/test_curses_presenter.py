import pytest

from src.data_models import CursesStates, Event
from src.interfaces import Presenter
from src.tui.presenters import CursesPresenter


class TestConstructor:
    @pytest.fixture(autouse=True)
    def setup(self, mock_view, mock_model, mock_presenter):
        self.view = mock_view
        self.model = mock_model
        self.multiplexer_menu = mock_presenter
        self.file_menu = mock_presenter
        self.command_bar = mock_presenter

    def test_given_valid_arguments_returns_instance_of_jmux_presenter(self):
        assert isinstance(
            CursesPresenter(
                self.view,
                self.model,
                self.multiplexer_menu,
                self.file_menu,
                self.command_bar,
            ),
            CursesPresenter,
        )

    def test_implements_presenter_interface(self):
        assert isinstance(
            CursesPresenter(
                self.view,
                self.model,
                self.multiplexer_menu,
                self.file_menu,
                self.command_bar,
            ),
            Presenter,
        )


class TestActivate:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, mock_presenter):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.multiplexer_menu = mock_presenter
        self.file_menu = mock_presenter
        self.command_bar = mock_presenter
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_runs_event_loop(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        assert self.presenter.activate() is None

    def test_gets_event(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        self.presenter.activate()
        self.presenter.get_event.assert_called()

    def test_runs_event_loop_until_exit_event(self):
        self.mocker.patch.object(
            self.presenter,
            "get_event",
            side_effect=[Event.NOOP, Event.NOOP, Event.EXIT],
        )
        self.presenter.activate()
        assert self.presenter.get_event.call_count == 3

    def test_calls_update_view(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        self.mocker.patch.object(self.presenter, "update_view")
        self.presenter.activate()
        self.presenter.update_view.assert_called()

    def test_calls_handle_event(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        self.mocker.patch.object(
            self.presenter,
            "handle_event",
            side_effect=lambda _: setattr(self.presenter, "active", False),
        )
        self.presenter.activate()
        self.presenter.handle_event.assert_called()


class TestDeactivate:
    def test_sets_active_to_false(self, mock_view, mock_model, mock_presenter):
        presenter = CursesPresenter(
            mock_view, mock_model, mock_presenter, mock_presenter, mock_presenter
        )
        presenter.active = True
        presenter.deactivate()
        assert presenter.active is False


class TestUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, mock_presenter):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.multiplexer_menu = mock_presenter
        self.file_menu = mock_presenter
        self.command_bar = mock_presenter
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_calls_command_bar_update_view(self):
        self.presenter.update_view()
        self.presenter.command_bar.update_view.assert_called()

    def test_calls_file_menu_update_view(self):
        self.presenter.update_view()
        self.presenter.file_menu.update_view.assert_called()

    def test_calls_multiplexer_menu_update_view(self):
        self.presenter.update_view()
        self.presenter.multiplexer_menu.update_view.assert_called()


class TestGetEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, mock_presenter):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.multiplexer_menu = mock_presenter
        self.file_menu = mock_presenter
        self.command_bar = mock_presenter
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_file_menu_state_calls_get_event_on_file_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.get_event()
        self.presenter.file_menu.get_event.assert_called()

    def test_multiplexer_menu_state_calls_get_event_on_multiplexer_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.get_event()
        self.presenter.multiplexer_menu.get_event.assert_called()

    def test_other_states_return_exit_event(self):
        self.presenter.state = "other"
        assert self.presenter.get_event() == Event.EXIT


class TestHandleEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model, mock_presenter):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.multiplexer_menu = mock_presenter
        self.file_menu = mock_presenter
        self.command_bar = mock_presenter
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_exit_event_deactivates_presenter(self):
        self.presenter.handle_event(Event.EXIT)
        assert self.presenter.active is False
