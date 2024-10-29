from typing import Any, Optional, Union

from src.data_models import Event
from src.interfaces import Model, Presenter, View


class CommandBarPresenter(Presenter[Optional[Union[bool, str]]]):
    def __init__(self, view: View, model: Model) -> None:
        """
        Presenter for the message window.
        """
        self.view = view
        self.model = model
        self.active = False
        self._validate_input()

    def _validate_input(self) -> None:
        if not isinstance(self.view, View):
            raise TypeError("View must implement the View interface")
        if not isinstance(self.model, Model):
            raise TypeError("Model must implement the Model interface")

    def activate(self) -> None:
        """
        Activate the presenter.
        """
        self.active = True

    def update_view(self) -> None:
        """
        Clear the message window.
        """
        self.view.render("")

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_command()

    def handle_event(self, event: Event, *args: Any) -> Optional[Union[bool, str]]:
        """
        Handle a given `event`.
        """
        match event:
            case Event.SHOW_MESSAGE:
                self.view.show_message(args[0])
            case Event.CONFIRM:
                return self.view.get_confirmation(args[0])
            case Event.INPUT:
                return self.view.get_input(args[0])
        return None
