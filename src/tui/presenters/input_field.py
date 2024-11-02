from typing import Tuple, Union

from src.data_models import Event, Key
from src.interfaces import Model, Presenter, View


class InputFieldPresenter(Presenter[Union[bool, str, None]]):
    def __init__(self, view: View[Key], model: Model) -> None:
        self.view: View[Key] = view
        self.model: Model = model
        self.active: bool = False
        self.cursor_pos: Tuple[int, int] = (0, 0)
        self.text: str = ""

    def activate(self) -> None:
        self.text = ""
        self.cursor_pos = (0, 0)
        self.active = True

    def deactivate(self) -> None:
        self.text = ""
        self.cursor_pos = (0, 0)
        self.active = False

    def update_view(self) -> None:
        pass

    def get_event(self) -> Event:
        return Event.NOOP

    def handle_event(
        self, event: Event, *args: str, is_error: bool = False
    ) -> Union[bool, str, None]:
        match event:
            case Event.SHOW_MESSAGE:
                self._show_message(args[0], is_error)
            case Event.CONFIRM:
                confirmation = self._confirm(args[0])
                self.deactivate()
                return confirmation
            case Event.INPUT:
                output = self._input(args[0])
                self.deactivate()
                if output:
                    return output
        return None

    def _show_message(self, message: str, is_error: bool = False) -> None:
        self.view.render(message, (0, 0), is_error=is_error)

    def _confirm(self, confirmation_prompt: str) -> bool:
        self.activate()
        self.view.render(confirmation_prompt, (0, len(confirmation_prompt)))
        self._handle_key_press(self.view.get_event())
        if self.text == "y" or self.text == "Y":
            return True
        return False

    def _input(self, prompt: str) -> str:
        self.activate()
        while self.active:
            self.view.render(
                prompt + self.text,
                (self.cursor_pos[0], len(prompt) + self.cursor_pos[1]),
            )
            self._handle_key_press(self.view.get_event())
        return self.text

    def _handle_key_press(self, key: Key) -> None:
        match key:
            case Key.UNKNOWN:
                pass
            case Key.ESC:
                self.deactivate()
            case Key.ENTER:
                self.active = False
            case Key.BACKSPACE:
                if self.cursor_pos[1] > 0:
                    if self.cursor_pos[1] < len(self.text):
                        self.text = (
                            self.text[: self.cursor_pos[1] - 1]
                            + self.text[self.cursor_pos[1] :]
                        )
                    else:
                        self.text = self.text[:-1]
                self._decrement_cursor()
            case Key.LEFT:
                self._decrement_cursor()
            case Key.RIGHT:
                if self.cursor_pos[1] < len(self.text):
                    self._increment_cursor()
            case _:
                if self.cursor_pos[1] < len(self.text):
                    self.text = (
                        self.text[: self.cursor_pos[1]]
                        + chr(key.value)
                        + self.text[self.cursor_pos[1] :]
                    )
                else:
                    self.text += chr(key.value)
                self._increment_cursor()

    def _increment_cursor(self) -> None:
        self.cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] + 1)

    def _decrement_cursor(self) -> None:
        if self.cursor_pos[1] > 0:
            self.cursor_pos = (self.cursor_pos[0], self.cursor_pos[1] - 1)
