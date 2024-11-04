from typing import List, Optional

from src.data_models import Event, SessionLabel
from src.interfaces import Model, Presenter, View


class FileMenuPresenter(Presenter[Optional[SessionLabel]]):
    def __init__(self, view: View[Event], model: Model) -> None:
        """
        Presenter for Menus.
        """
        self.view: View[Event] = view
        self.model: Model = model
        self.cursor_position: int = 0
        self.active: bool = False
        self.sessions: List[SessionLabel] = self.model.list_saved_sessions()

    def toggle_active(self) -> None:
        """
        Activate the presenter.
        """
        self.active = not self.active

    def update_view(self) -> None:
        """
        Get data from the model and update the view.
        """
        self.sessions = self.model.list_saved_sessions()
        self._check_cursor_position()
        annotated_sessions = [
            self._annotate_session(index, session)
            for index, session in enumerate(self.sessions)
        ]
        self.view.render(
            annotated_sessions,
            self.cursor_position,
            self.active,
        )

    def _annotate_session(self, index: int, session: SessionLabel) -> str:
        name = f"{index + 1}. {session.name}"
        if session == self.model.get_active_session():
            name += "*"
        if (
            session in self.model.list_running_sessions()
            and session in self.model.list_saved_sessions()
        ):
            name += " (running)"
        return name

    def get_event(self) -> Event:
        """
        Get event from the view.
        """
        return self.view.get_event()

    def handle_event(self, event: Event) -> Optional[SessionLabel]:
        """
        Handle a given `event`.
        """
        match event:
            case Event.MOVE_UP:
                self._cursor_up()
            case Event.MOVE_DOWN:
                self._cursor_down()
            case Event.GET_SESSION:
                return self.sessions[self.cursor_position]
        return None

    def _cursor_up(self) -> None:
        self.cursor_position -= 1
        self._check_cursor_position()

    def _cursor_down(self) -> None:
        self.cursor_position += 1
        self._check_cursor_position()

    def _check_cursor_position(self) -> None:
        if self.cursor_position >= len(self.sessions):
            self.cursor_position = len(self.sessions) - 1
        if self.cursor_position < 0:
            self.cursor_position = 0
