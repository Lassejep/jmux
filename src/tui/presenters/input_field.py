from typing import Any, Tuple, Union

from src.data_models import Event, Key
from src.interfaces import Model, Presenter, View


class InputFieldPresenter(Presenter[Event, Union[bool, str, None]]):
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
        self.active = False

    def update_view(self) -> None:
        pass

    def get_event(self) -> Event:
        return Event.NOOP

    def handle_event(self, event: Event, *args: Any) -> Union[bool, str, None]:
        match event:
            case Event.SHOW_MESSAGE:
                self.view.render(args[0], (0, 0))
                if args[0].startswith("Error:"):
                    self.view.render(args[0], (0, 0), is_error=True)
            case Event.CONFIRM:
                self.activate()
                self.view.render(args[0], (0, len(args[0])))
                self.handle_key_press(self.view.get_event())
                self.deactivate()
                if self.text == "y":
                    return True
                return False
            case Event.INPUT:
                self.activate()
                while self.active:
                    self.view.render(
                        args[0] + self.text,
                        (self.cursor_pos[0], len(args[0]) + self.cursor_pos[1]),
                    )
                    self.handle_key_press(self.view.get_event())
                if self.text:
                    return self.text
            case _:
                pass
        return None

    def handle_key_press(self, key: Key) -> None:
        match key:
            case Key.UNKNOWN:
                pass
            case Key.ESC:
                self.text = ""
                self.deactivate()
            case Key.ENTER:
                self.deactivate()
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
