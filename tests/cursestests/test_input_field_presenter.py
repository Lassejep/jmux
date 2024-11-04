import pytest

from src.data_models import Event, Key
from src.interfaces import Presenter
from src.tui.presenters import InputFieldPresenter


class TestConstructor:
    def test_given_valid_arguments_returns_instance_of_input_field_presenter(
        self, mock_view, mock_model
    ):
        assert isinstance(
            InputFieldPresenter(mock_view, mock_model), InputFieldPresenter
        )

    def test_implements_presenter_interface(self, mock_view, mock_model):
        assert isinstance(InputFieldPresenter(mock_view, mock_model), Presenter)


class TestToggleActive:
    @pytest.fixture(autouse=True)
    def setup(self, mock_view, mock_model):
        self.view = mock_view
        self.model = mock_model
        self.presenter = InputFieldPresenter(self.view, self.model)

    def test_toggles_active_state(self):
        self.presenter.active = False
        self.presenter.toggle_active()
        assert self.presenter.active is True
        self.presenter.toggle_active()
        assert self.presenter.active is False

    def resets_input_field(self):
        self.presenter.input_field = "test"
        self.presenter.toggle_active()
        assert self.presenter.input_field == ""

    def resets_cursor_position(self):
        self.presenter.cursor_position = (10, 10)
        self.presenter.toggle_active()
        assert self.presenter.cursor_position == (0, 0)


class TestGetEvent:
    def test_returns_noop_event(self, mock_view, mock_model):
        presenter = InputFieldPresenter(mock_view, mock_model)
        assert presenter.get_event() == Event.NOOP


class TestHandleShowMessageEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.presenter = InputFieldPresenter(self.view, self.model)

    def test_given_message_renders_message_not_as_error(self):
        self.presenter.handle_event(Event.SHOW_MESSAGE, "test")
        self.view.render.assert_called_once_with("test", (0, 0), is_error=False)

    def test_given_message_and_error_flag_renders_message_as_error(self):
        self.presenter.handle_event(Event.SHOW_MESSAGE, "test", is_error=True)
        self.view.render.assert_called_once_with("test", (0, 0), is_error=True)


class TestHandleConfirmEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.presenter = InputFieldPresenter(self.view, self.model)

    def test_activates_input_field(self):
        self.mocker.patch.object(self.presenter, "toggle_active")
        self.presenter.handle_event(Event.CONFIRM, "test")
        self.presenter.toggle_active.assert_called_once()

    def test_renders_prompt(self):
        self.presenter.handle_event(Event.CONFIRM, "test")
        self.view.render.assert_called_once_with("test", (0, len("test")))

    def test_passes_prompt_length_as_cursor_position(self):
        self.presenter.handle_event(Event.CONFIRM, "test")
        self.view.render.assert_called_once_with("test", (0, len("test")))
        self.presenter.handle_event(Event.CONFIRM, "test123")
        self.view.render.assert_called_with("test123", (0, len("test123")))

    def test_returns_true_if_input_is_y(self):
        self.view.get_event.return_value = Key.Y_LOWER
        assert self.presenter.handle_event(Event.CONFIRM, "test") is True
        self.view.get_event.return_value = Key.Y_UPPER
        assert self.presenter.handle_event(Event.CONFIRM, "test") is True

    test_inputs = [
        test_key for test_key in Key if test_key not in [Key.Y_LOWER, Key.Y_UPPER]
    ]

    @pytest.mark.parametrize("key", test_inputs)
    def test_returns_false_when_input_is_not_y(self, key):
        self.view.get_event.return_value = key
        assert self.presenter.handle_event(Event.CONFIRM, "test") is False

    def test_deactivates_input_field(self):
        self.presenter.handle_event(Event.CONFIRM, "test")
        assert self.presenter.active is False


class TestHandleInputEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.presenter = InputFieldPresenter(self.view, self.model)

    def test_activates_input_field(self):
        self.mocker.patch.object(self.presenter, "toggle_active")
        self.presenter.handle_event(Event.INPUT, "test")
        self.presenter.toggle_active.assert_called_once()

    def test_renders_prompt(self):
        self.view.get_event.return_value = Key.ENTER
        self.presenter.handle_event(Event.INPUT, "test")
        self.view.render.assert_called_once_with("test", (0, len("test")))

    def test_passes_prompt_length_as_cursor_position(self):
        self.view.get_event.return_value = Key.ENTER
        self.presenter.handle_event(Event.INPUT, "test")
        self.view.render.assert_called_once_with("test", (0, len("test")))
        self.presenter.handle_event(Event.INPUT, "test123")
        self.view.render.assert_called_with("test123", (0, len("test123")))

    def test_returns_none_when_no_character_entered(self):
        self.view.get_event.return_value = Key.ENTER
        assert self.presenter.handle_event(Event.INPUT, "test") is None

    def test_returns_input_when_enter_key_pressed(self):
        self.view.get_event.side_effect = [Key.A_LOWER, Key.ENTER]
        assert self.presenter.handle_event(Event.INPUT, "test") == "a"

    def test_returns_input_when_multiple_characters_entered(self):
        self.view.get_event.side_effect = [Key.A_LOWER, Key.B_LOWER, Key.ENTER]
        assert self.presenter.handle_event(Event.INPUT, "test") == "ab"

    def test_renders_prompt_with_current_input_characters(self):
        self.view.get_event.side_effect = [Key.A_LOWER, Key.ENTER]
        self.presenter.handle_event(Event.INPUT, "test")
        self.view.render.assert_called_with("testa", (0, len("testa")))

    def test_renders_prompt_with_cursor_position_at_end_of_input(self):
        self.view.get_event.side_effect = [Key.A_LOWER, Key.ENTER]
        self.presenter.handle_event(Event.INPUT, "test")
        self.view.render.assert_called_with("testa", (0, len("testa")))

    def test_deactivates_input_field(self):
        self.view.get_event.return_value = Key.ENTER
        self.presenter.handle_event(Event.INPUT, "test")
        assert self.presenter.active is False

    def test_returns_none_when_escape_key_pressed(self):
        self.view.get_event.side_effect = [Key.A_LOWER, Key.ESC]
        assert self.presenter.handle_event(Event.INPUT, "test") is None

    def test_backspace_at_beginning_of_input_does_nothing(self):
        self.view.get_event.side_effect = [Key.BACKSPACE, Key.A_LOWER, Key.ENTER]
        assert self.presenter.handle_event(Event.INPUT, "test") == "a"

    def test_backspace_at_end_of_input_removes_last_character(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.B_LOWER,
            Key.BACKSPACE,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "a"

    def test_left_arrow_key_decrements_cursor_position(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.LEFT,
            Key.B_LOWER,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "ba"

    def test_left_arrow_key_does_not_decrement_cursor_position_below_zero(self):
        self.view.get_event.side_effect = [Key.LEFT, Key.A_LOWER, Key.ENTER]
        assert self.presenter.handle_event(Event.INPUT, "test") == "a"

    def test_right_arrow_key_increments_cursor_position(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.LEFT,
            Key.B_LOWER,
            Key.RIGHT,
            Key.C_LOWER,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "bac"

    def test_right_arrow_key_does_not_increment_cursor_position_above_max(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.RIGHT,
            Key.B_LOWER,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "ab"

    def test_unknown_key_does_nothing(self):
        self.view.get_event.side_effect = [Key.UNKNOWN, Key.A_LOWER, Key.ENTER]
        assert self.presenter.handle_event(Event.INPUT, "test") == "a"

    def test_unknown_key_does_not_increment_cursor_position(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.LEFT,
            Key.UNKNOWN,
            Key.B_LOWER,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "ba"

    def test_unknown_key_does_not_decrement_cursor_position(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.UNKNOWN,
            Key.B_LOWER,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "ab"

    def test_backspace_key_removes_character_at_cursor_position(self):
        self.view.get_event.side_effect = [
            Key.A_LOWER,
            Key.B_LOWER,
            Key.LEFT,
            Key.BACKSPACE,
            Key.ENTER,
        ]
        assert self.presenter.handle_event(Event.INPUT, "test") == "b"

    test_keys = [
        key
        for key in Key
        if key
        not in [Key.ENTER, Key.BACKSPACE, Key.LEFT, Key.RIGHT, Key.ESC, Key.UNKNOWN]
    ]

    @pytest.mark.parametrize("key", test_keys)
    def test_keys_returned_as_input(self, key):
        self.view.get_event.side_effect = [key, Key.ENTER]
        assert self.presenter.handle_event(Event.INPUT, "test") == chr(key.value)


class TestHandleEvent:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, mock_view, mock_model):
        self.mocker = mocker
        self.view = mock_view
        self.model = mock_model
        self.presenter = InputFieldPresenter(self.view, self.model)

    def test_calls_show_message(self):
        self.mocker.patch.object(self.presenter, "_show_message")
        self.presenter.handle_event(Event.SHOW_MESSAGE, "test")
        self.presenter._show_message.assert_called_once_with("test", False)
        self.presenter.handle_event(Event.SHOW_MESSAGE, "test", is_error=True)
        self.presenter._show_message.assert_called_with("test", True)

    def test_calls_confirm(self):
        self.mocker.patch.object(self.presenter, "_confirm")
        self.presenter.handle_event(Event.CONFIRM, "test")
        self.presenter._confirm.assert_called_once_with("test")

    def test_calls_input(self):
        self.mocker.patch.object(self.presenter, "_input")
        self.presenter.handle_event(Event.INPUT, "test")
        self.presenter._input.assert_called_once_with("test")

    test_events = [
        event
        for event in Event
        if event not in [Event.SHOW_MESSAGE, Event.CONFIRM, Event.INPUT]
    ]

    @pytest.mark.parametrize("event", test_events)
    def test_returns_none_for_other_events(self, event):
        assert self.presenter.handle_event(event) is None
