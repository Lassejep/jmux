import pytest

from src.data_models import CursesStates, Event
from src.interfaces import Model, Presenter, View
from src.tui.presenters import CursesPresenter


class TestConstructor:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.view = mocker.Mock(spec=View)
        self.model = mocker.Mock(spec=Model)
        self.multiplexer_menu = mocker.Mock(spec=Presenter)
        self.file_menu = mocker.Mock(spec=Presenter)
        self.command_bar = mocker.Mock(spec=Presenter)

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


class TestToggleActive:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_runs_event_loop(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        assert self.presenter.toggle_active() is None

    def test_gets_event(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        self.presenter.toggle_active()
        self.presenter.get_event.assert_called()

    def test_handles_event(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        self.mocker.patch.object(
            self.presenter,
            "handle_event",
            side_effect=lambda _: setattr(self.presenter, "active", False),
        )
        self.presenter.toggle_active()
        self.presenter.handle_event.assert_called()

    def test_updates_view(self):
        self.mocker.patch.object(self.presenter, "get_event", return_value=Event.EXIT)
        self.mocker.patch.object(self.presenter, "update_view")
        self.presenter.toggle_active()
        self.presenter.update_view.assert_called()

    def test_runs_event_loop_until_exit_event(self):
        self.mocker.patch.object(
            self.presenter,
            "get_event",
            side_effect=[Event.NOOP, Event.NOOP, Event.EXIT],
        )
        self.presenter.toggle_active()
        assert self.presenter.get_event.call_count == 3


class TestUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
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
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
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


class TestHandleQuitEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
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


class TestHandleMoveLeftEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_file_menu_state_moves_to_multiplexer_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.MOVE_LEFT)
        assert self.presenter.state == CursesStates.MULTIPLEXER_MENU

    def test_multiplexer_menu_state_does_not_change(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.MOVE_LEFT)
        assert self.presenter.state == CursesStates.MULTIPLEXER_MENU

    def test_activates_multiplexer_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.MOVE_LEFT)
        self.presenter.multiplexer_menu.toggle_active.assert_called()

    def test_deactivates_file_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.MOVE_LEFT)
        self.presenter.file_menu.toggle_active.assert_called()


class TestHandleMoveRightEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_multiplexer_menu_state_moves_to_file_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.MOVE_RIGHT)
        assert self.presenter.state == CursesStates.FILE_MENU

    def test_file_menu_state_does_not_change(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.MOVE_RIGHT)
        assert self.presenter.state == CursesStates.FILE_MENU

    def test_activates_file_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.MOVE_RIGHT)
        self.presenter.file_menu.toggle_active.assert_called()

    def test_deactivates_multiplexer_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.MOVE_RIGHT)
        self.presenter.multiplexer_menu.toggle_active.assert_called()


class TestHandleMoveUpEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_calls_move_up_on_active_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.MOVE_UP)
        self.presenter.file_menu.handle_event.assert_called_with(Event.MOVE_UP)

    def test_does_not_call_move_up_on_inactive_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.MOVE_UP)
        self.presenter.multiplexer_menu.handle_event.assert_called_with(Event.MOVE_UP)
        self.presenter.file_menu.handle_event.assert_not_called()


class TestHandleMoveDownEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_calls_move_down_on_active_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.MOVE_DOWN)
        self.presenter.file_menu.handle_event.assert_called_with(Event.MOVE_DOWN)

    def test_does_not_call_move_down_on_inactive_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.MOVE_DOWN)
        self.presenter.multiplexer_menu.handle_event.assert_called_with(Event.MOVE_DOWN)
        self.presenter.file_menu.handle_event.assert_not_called()


class TestHandleLoadSessionEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_gets_session_from_correct_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.LOAD_SESSION)
        self.presenter.file_menu.handle_event.assert_called_with(Event.GET_SESSION)

    def test_does_not_get_session_from_incorrect_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.LOAD_SESSION)
        self.presenter.file_menu.handle_event.assert_not_called()

    def test_invalid_session_shows_error_message_in_command_bar(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = None
        self.presenter.handle_event(Event.LOAD_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_loads_session_from_model(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.handle_event(Event.LOAD_SESSION)
        self.presenter.model.load_session.assert_called_with(session_labels[0])

    def test_failure_to_load_session_shows_error_message_in_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.load_session.side_effect = ValueError("Test Error")
        self.presenter.handle_event(Event.LOAD_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[0][1] == "Test Error"
        assert error_call_args[1]["is_error"] is True


class TestHandleCreateSessionEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_gets_new_name_from_command_bar(self):
        self.presenter.handle_event(Event.CREATE_SESSION)
        calls = self.presenter.command_bar.handle_event.call_args_list
        assert calls[0][0][0] == Event.INPUT

    def test_does_not_create_session_if_no_name_provided(self):
        self.presenter.command_bar.handle_event.return_value = ""
        self.presenter.handle_event(Event.CREATE_SESSION)
        self.presenter.model.create_session.assert_not_called()

    def test_no_name_provided_shows_error_message_in_command_bar(self):
        self.presenter.command_bar.handle_event.return_value = ""
        self.presenter.handle_event(Event.CREATE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[1]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_creates_session_with_new_name(self):
        self.presenter.command_bar.handle_event.return_value = "test_session"
        self.presenter.handle_event(Event.CREATE_SESSION)
        self.presenter.model.create_session.assert_called_with("test_session")

    def test_failure_to_create_session_shows_error_message_in_command_bar(self):
        self.presenter.command_bar.handle_event.return_value = "test_session"
        self.presenter.model.create_session.side_effect = ValueError("Test Error")
        self.presenter.handle_event(Event.CREATE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[0][1] == "Test Error"
        assert error_call_args[1]["is_error"] is True


class TestHandleKillSessionEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_gets_session_from_correct_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.KILL_SESSION)
        self.presenter.multiplexer_menu.handle_event.assert_called_with(
            Event.GET_SESSION
        )

    def test_does_not_get_session_from_incorrect_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.KILL_SESSION)
        self.presenter.multiplexer_menu.handle_event.assert_not_called()

    def test_invalid_session_shows_error_message_in_command_bar(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = None
        self.presenter.handle_event(Event.KILL_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_gets_confirmation_from_command_bar(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.handle_event(Event.KILL_SESSION)
        confirm_call = self.presenter.command_bar.handle_event.call_args_list[0]
        assert confirm_call[0][0] == Event.CONFIRM

    def test_does_not_kill_session_if_no_confirmation(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.KILL_SESSION)
        self.presenter.model.kill_session.assert_not_called()

    def test_no_confirmation_shows_error_message_in_command_bar(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.KILL_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[1]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_kills_session(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = True
        self.presenter.handle_event(Event.KILL_SESSION)
        self.presenter.model.kill_session.assert_called_with(session_labels[0])

    def test_failure_to_kill_session_shows_error_message_in_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = True
        self.presenter.model.kill_session.side_effect = ValueError("Test Error")
        self.presenter.handle_event(Event.KILL_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[0][1] == "Test Error"
        assert error_call_args[1]["is_error"] is True


class TestHandleSaveSessionEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_gets_session_from_correct_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.SAVE_SESSION)
        self.presenter.multiplexer_menu.handle_event.assert_called_with(
            Event.GET_SESSION
        )

    def test_does_not_get_session_from_incorrect_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.SAVE_SESSION)
        self.presenter.multiplexer_menu.handle_event.assert_not_called()

    def test_invalid_session_shows_error_message_in_command_bar(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = None
        self.presenter.handle_event(Event.SAVE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_if_session_is_already_saved_gets_confirmation_from_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.list_saved_sessions.return_value = session_labels
        self.presenter.handle_event(Event.SAVE_SESSION)
        confirm_call = self.presenter.command_bar.handle_event.call_args_list[0]
        assert confirm_call[0][0] == Event.CONFIRM

    def test_does_not_save_session_if_no_confirmation(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.list_saved_sessions.return_value = session_labels
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.SAVE_SESSION)
        self.presenter.model.save_session.assert_not_called()

    def test_no_confirmation_shows_error_message_in_command_bar(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.list_saved_sessions.return_value = session_labels
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.SAVE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[1]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_session_not_already_saved_does_not_get_confirmation_from_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.list_saved_sessions.return_value = []
        self.presenter.handle_event(Event.SAVE_SESSION)
        self.presenter.command_bar.handle_event.assert_not_called()

    def test_saves_session(self, session_labels):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.list_saved_sessions.return_value = []
        self.presenter.handle_event(Event.SAVE_SESSION)
        self.presenter.model.save_session.assert_called_with(session_labels[0])

    def test_failure_to_save_session_shows_error_message_in_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.multiplexer_menu.handle_event.return_value = session_labels[0]
        self.presenter.model.list_saved_sessions.return_value = []
        self.presenter.model.save_session.side_effect = ValueError("Test Error")
        self.presenter.handle_event(Event.SAVE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[0][1] == "Test Error"
        assert error_call_args[1]["is_error"] is True


class TestHandleDeleteSessionEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_gets_session_from_correct_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.DELETE_SESSION)
        self.presenter.file_menu.handle_event.assert_called_with(Event.GET_SESSION)

    def test_does_not_get_session_from_incorrect_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.DELETE_SESSION)
        self.presenter.file_menu.handle_event.assert_not_called()

    def test_invalid_session_shows_error_message_in_command_bar(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = None
        self.presenter.handle_event(Event.DELETE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_gets_confirmation_from_command_bar(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.handle_event(Event.DELETE_SESSION)
        confirm_call = self.presenter.command_bar.handle_event.call_args_list[0]
        assert confirm_call[0][0] == Event.CONFIRM

    def test_does_not_delete_session_if_no_confirmation(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.DELETE_SESSION)
        self.presenter.model.delete_session.assert_not_called()

    def test_no_confirmation_shows_error_message_in_command_bar(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.DELETE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[1]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_deletes_session(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = True
        self.presenter.handle_event(Event.DELETE_SESSION)
        self.presenter.model.delete_session.assert_called_with(session_labels[0])

    def test_failure_to_delete_session_shows_error_message_in_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = True
        self.presenter.model.delete_session.side_effect = ValueError("Test Error")
        self.presenter.handle_event(Event.DELETE_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[0][1] == "Test Error"
        assert error_call_args[1]["is_error"] is True


class TestHandleRenameSessionEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.mocker = mocker
        self.view = self.mocker.Mock(spec=View)
        self.model = self.mocker.Mock(spec=Model)
        self.multiplexer_menu = self.mocker.Mock(spec=Presenter)
        self.file_menu = self.mocker.Mock(spec=Presenter)
        self.command_bar = self.mocker.Mock(spec=Presenter)
        self.presenter = CursesPresenter(
            self.view,
            self.model,
            self.multiplexer_menu,
            self.file_menu,
            self.command_bar,
        )

    def test_gets_session_from_correct_menu(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.presenter.handle_event(Event.RENAME_SESSION)
        self.presenter.file_menu.handle_event.assert_called_with(Event.GET_SESSION)

    def test_does_not_get_session_from_incorrect_menu(self):
        self.presenter.state = CursesStates.MULTIPLEXER_MENU
        self.presenter.handle_event(Event.RENAME_SESSION)
        self.presenter.file_menu.handle_event.assert_not_called()

    def test_invalid_session_shows_error_message_in_command_bar(self):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = None
        self.presenter.handle_event(Event.RENAME_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_gets_confirmation_from_command_bar(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.handle_event(Event.RENAME_SESSION)
        confirm_call = self.presenter.command_bar.handle_event.call_args_list[0]
        assert confirm_call[0][0] == Event.CONFIRM

    def test_does_not_rename_session_if_no_confirmation(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.RENAME_SESSION)
        self.presenter.model.rename_session.assert_not_called()

    def test_no_confirmation_shows_error_message_in_command_bar(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.return_value = False
        self.presenter.handle_event(Event.RENAME_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[1]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_gets_new_name_from_command_bar(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.side_effect = [True, "new_name"]
        self.presenter.handle_event(Event.RENAME_SESSION)
        input_call = self.presenter.command_bar.handle_event.call_args_list[1]
        assert input_call[0][0] == Event.INPUT

    def test_does_not_rename_session_if_no_new_name_provided(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.side_effect = [True, "", "error"]
        self.presenter.handle_event(Event.RENAME_SESSION)
        self.presenter.model.rename_session.assert_not_called()

    def test_no_new_name_provided_shows_error_message_in_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.side_effect = [True, "", "error"]
        self.presenter.handle_event(Event.RENAME_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[2]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[1]["is_error"] is True

    def test_renames_session(self, session_labels):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.side_effect = [True, "new_name"]
        self.presenter.handle_event(Event.RENAME_SESSION)
        self.presenter.model.rename_session.assert_called_with(
            session_labels[0], "new_name"
        )

    def test_failure_to_rename_session_shows_error_message_in_command_bar(
        self, session_labels
    ):
        self.presenter.state = CursesStates.FILE_MENU
        self.file_menu.handle_event.return_value = session_labels[0]
        self.presenter.command_bar.handle_event.side_effect = [True, "new_name", None]
        self.presenter.model.rename_session.side_effect = ValueError("Test Error")
        self.presenter.handle_event(Event.RENAME_SESSION)
        error_call_args = self.presenter.command_bar.handle_event.call_args_list[2]
        assert error_call_args[0][0] == Event.SHOW_MESSAGE
        assert error_call_args[0][1] == "Test Error"
        assert error_call_args[1]["is_error"] is True


class TestHandleUnknownEvent:
    def test_does_nothing(self, mock_view, mock_model, mock_presenter):
        presenter = CursesPresenter(
            mock_view, mock_model, mock_presenter, mock_presenter, mock_presenter
        )
        presenter.handle_event(Event.UNKNOWN)
        assert True


class TestHandleInvalidEvent:
    def test_shows_error_message_in_command_bar(
        self, mock_view, mock_model, mock_presenter
    ):
        presenter = CursesPresenter(
            mock_view, mock_model, mock_presenter, mock_presenter, mock_presenter
        )
        presenter.handle_event(Event.NOOP)
        call_args = presenter.command_bar.handle_event.call_args
        assert call_args[0][0] == Event.SHOW_MESSAGE
        assert call_args[1]["is_error"] is True
