from typing import Any, Optional

from src.data_models import Event, SessionLabel
from src.interfaces import Model, Presenter, SessionHandler, View


class MenuPresenter(Presenter[Optional[SessionLabel]]):
    def __init__(
        self, view: View, model: Model, session_handler: SessionHandler
    ) -> None:
        """
        Presenter for Menus.
        """
        self.view = view
        self.model = model
        self.session_handler: SessionHandler = session_handler
        self.cursor_position = 0
        self.active = False
        self._validate_input()

    def _validate_input(self) -> None:
        if not isinstance(self.view, View):
            raise TypeError("View must implement the View interface")
        if not isinstance(self.model, Model):
            raise TypeError("Model must implement the Model interface")
        if not isinstance(self.session_handler, SessionHandler):
            raise TypeError("SessionHandler must be an instance of SessionHandler")

    def activate(self) -> None:
        """
        Activate the presenter.
        """
        self.active = True

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self.sessions = self.session_handler.update_sessions()
        self.view.render(
            self.session_handler.get_annotated_sessions(),
            self.cursor_position,
            self.active,
        )

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_command()

    def handle_event(self, event: Event, *args: Any) -> Optional[SessionLabel]:
        """
        Handle a given `event`.
        """
        match event:
            case Event.MOVE_UP:
                self._cursor_up()
            case Event.MOVE_DOWN:
                self._cursor_down()
            case Event.GET_SESSION:
                return self.session_handler.sessions[self.cursor_position]
        return None

    def _cursor_up(self) -> None:
        if self.cursor_position > 0:
            self.cursor_position -= 1
        else:
            self.cursor_position = 0

    def _cursor_down(self) -> None:
        if self.cursor_position < len(self.sessions) - 1:
            self.cursor_position += 1
        else:
            self.cursor_position = len(self.sessions) - 1
